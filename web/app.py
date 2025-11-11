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
    Nhận dạng biển số từ mảng ảnh numpy với tất cả các bước trung gian
    
    Args:
        img_array: Mảng ảnh numpy (BGR)
        
    Returns:
        results: Danh sách kết quả
        plate_images: Danh sách ảnh biển số
        detected_image: Ảnh với vùng phát hiện
        processing_steps: Dictionary chứa tất cả bước xử lý
    """
    results = []
    plate_images = []
    processing_steps = {}
    
    # Bước 0: Resize ảnh về kích thước chuẩn
    img = detector.resize_image(img_array)
    img_original = img.copy()
    processing_steps['original'] = img_original.copy()
    
    # === PREPROCESSING ===
    
    # Bước 1: Chuyển đổi sang HSV và trích xuất Value (Grayscale)
    img_grayscale = preprocessor.extract_value(img)
    processing_steps['grayscale'] = cv2.cvtColor(img_grayscale, cv2.COLOR_GRAY2BGR)
    
    # Bước 2: Tăng độ tương phản (Top Hat + Black Hat)
    img_max_contrast = preprocessor.maximize_contrast(img_grayscale)
    processing_steps['contrast'] = cv2.cvtColor(img_max_contrast, cv2.COLOR_GRAY2BGR)
    
    # Bước 3: Làm mịn bằng Gaussian blur
    img_blurred = cv2.GaussianBlur(
        img_max_contrast, 
        preprocessor.GAUSSIAN_SMOOTH_FILTER_SIZE, 
        0
    )
    processing_steps['blurred'] = cv2.cvtColor(img_blurred, cv2.COLOR_GRAY2BGR)
    
    # Bước 4: Nhị phân hóa bằng Adaptive Threshold
    img_thresh = cv2.adaptiveThreshold(
        img_blurred,
        255.0,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        preprocessor.ADAPTIVE_THRESH_BLOCK_SIZE,
        preprocessor.ADAPTIVE_THRESH_WEIGHT
    )
    processing_steps['threshold'] = cv2.cvtColor(img_thresh, cv2.COLOR_GRAY2BGR)
    
    # === DETECTION ===
    
    # Bước 5: Phát hiện cạnh bằng Canny
    canny_image = detector.detect_edges(img_thresh)
    processing_steps['canny'] = cv2.cvtColor(canny_image, cv2.COLOR_GRAY2BGR)
    
    # Bước 6: Dilation để nối các cạnh bị đứt đoạn
    dilated_image = detector.dilate_edges(canny_image)
    processing_steps['dilated'] = cv2.cvtColor(dilated_image, cv2.COLOR_GRAY2BGR)
    
    # Bước 7: Tìm contour
    plate_contours = detector.find_plate_contours(dilated_image)
    
    # Vẽ contour lên ảnh gốc
    detected_image = img_original.copy()
    for contour in plate_contours:
        cv2.drawContours(detected_image, [contour], -1, (0, 255, 0), 3)
    processing_steps['contours'] = detected_image.copy()
    
    # Bước 8: Trích xuất vùng biển số
    plates = []
    img_original_for_crop = img.copy()
    
    for contour in plate_contours:
        roi, roi_thresh, angle = detector.extract_plate_region(
            img_original_for_crop, img_grayscale, img_thresh, contour
        )
        if roi is not None and roi_thresh is not None:
            plates.append((roi, roi_thresh))
    
    if len(plates) == 0:
        return results, plate_images, detected_image, processing_steps
    
    # === RECOGNITION ===
    
    # Bước 9: Nhận dạng từng biển số
    for idx, (roi, roi_thresh) in enumerate(plates):
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
    
    return results, plate_images, detected_image, processing_steps


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
        results, plate_images, detected_image, processing_steps = recognize_plate_from_array(img)
        
        # Chuyển đổi ảnh sang base64
        detected_img_resized = cv2.resize(detected_image, None, fx=0.5, fy=0.5)
        detected_img_base64 = encode_image_to_base64(detected_img_resized)
        
        plate_images_base64 = []
        for plate_img in plate_images:
            plate_resized = cv2.resize(plate_img, None, fx=0.75, fy=0.75)
            plate_images_base64.append(encode_image_to_base64(plate_resized))
        
        # Chuyển đổi các bước xử lý sang base64
        steps_base64 = {}
        for step_name, step_img in processing_steps.items():
            step_resized = cv2.resize(step_img, None, fx=0.3, fy=0.3)
            steps_base64[step_name] = encode_image_to_base64(step_resized)
        
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
            'processing_steps': steps_base64,
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

