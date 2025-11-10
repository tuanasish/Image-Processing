"""
Web UI for Vietnamese License Plate Recognition System
Flask application
"""

import os
import sys
import io
import base64
from pathlib import Path

from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np

# Thêm src vào path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.preprocessing import ImagePreprocessor
from src.detection import PlateDetector
from src.recognition import CharacterSegmenter, CharacterRecognizer
from src.utils import Config

# Cấu hình Flask với đường dẫn đúng
WEB_DIR = Path(__file__).resolve().parent
app = Flask(__name__, 
            template_folder=str(WEB_DIR / 'templates'),
            static_folder=str(WEB_DIR / 'static'))

app.config['UPLOAD_FOLDER'] = WEB_DIR / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Tạo thư mục nếu chưa có
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
Config.ensure_directories()

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# Khởi tạo các module
print("Initializing License Plate Recognition System...")
try:
    preprocessor = ImagePreprocessor()
    detector = PlateDetector()
    segmenter = CharacterSegmenter()
    recognizer = CharacterRecognizer(
        model_path=str(Config.MODEL_DIR),
        classifications_file=Config.CLASSIFICATIONS_FILE,
        flattened_images_file=Config.FLATTENED_IMAGES_FILE
    )
    print("System initialized successfully!")
except Exception as e:
    print(f"Error initializing system: {e}")
    sys.exit(1)


def encode_image_to_base64(img):
    """
    Chuyển đổi ảnh OpenCV sang base64 string
    
    Args:
        img: Ảnh OpenCV (numpy array)
        
    Returns:
        img_base64: String base64
    """
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64


def recognize_plate_from_array(img_array):
    """
    Nhận dạng biển số từ mảng ảnh numpy
    
    Args:
        img_array: Mảng ảnh numpy (BGR)
        
    Returns:
        results: Danh sách kết quả
        plate_images: Danh sách ảnh biển số
        detected_image: Ảnh với vùng phát hiện
    """
    results = []
    plate_images = []
    
    # Resize ảnh về kích thước chuẩn
    img = detector.resize_image(img_array)
    img_original = img.copy()
    
    # Preprocessing
    img_grayscale, img_thresh = preprocessor.preprocess(img)
    
    # Detection
    plates, contours = detector.detect_plates(img, img_grayscale, img_thresh)
    
    # Vẽ contour lên ảnh gốc
    detected_image = img_original.copy()
    for contour in contours:
        cv2.drawContours(detected_image, [contour], -1, (0, 255, 0), 3)
    
    if len(plates) == 0:
        return results, plate_images, detected_image
    
    # Recognition
    for roi, roi_thresh in plates:
        try:
            # Segment characters
            characters, _ = segmenter.segment_characters(roi_thresh)
            
            if len(characters) == 0:
                continue
            
            # Classify lines
            height, width = roi_thresh.shape[:2]
            first_line_chars, second_line_chars = segmenter.classify_lines(
                characters, height
            )
            
            # Recognize
            plate_text = recognizer.recognize_plate(
                first_line_chars, second_line_chars
            )
            
            if plate_text:
                results.append(plate_text)
                
                # Vẽ ký tự đã nhận dạng lên ảnh biển số
                roi_display = roi.copy()
                for char in characters:
                    x, y, w, h, _ = char
                    cv2.rectangle(roi_display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                plate_images.append(roi_display)
        
        except Exception as e:
            print(f"Error processing plate: {e}")
            continue
    
    return results, plate_images, detected_image


@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')


@app.route('/api/recognize', methods=['POST'])
def recognize():
    """API nhận dạng biển số"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Không có file được upload'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Chưa chọn file'}), 400
        
        # Đọc ảnh
        file_bytes = file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Không thể đọc ảnh. Vui lòng chọn file ảnh hợp lệ.'}), 400
        
        # Nhận dạng biển số
        results, plate_images, detected_image = recognize_plate_from_array(img)
        
        # Chuyển đổi ảnh sang base64
        detected_img_resized = cv2.resize(detected_image, None, fx=0.5, fy=0.5)
        detected_img_base64 = encode_image_to_base64(detected_img_resized)
        
        plate_images_base64 = []
        for plate_img in plate_images:
            plate_resized = cv2.resize(plate_img, None, fx=0.75, fy=0.75)
            plate_images_base64.append(encode_image_to_base64(plate_resized))
        
        # Format kết quả
        if results:
            result_text = " | ".join(results)
        else:
            result_text = "Không phát hiện được biển số"
        
        return jsonify({
            'success': True,
            'results': results,
            'result_text': result_text,
            'detected_image': detected_img_base64,
            'plate_images': plate_images_base64,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'Lỗi xử lý: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'System is running'})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Web UI - Vietnamese License Plate Recognition System")
    print("="*60)
    print("Open your browser and visit: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)

