"""
Vietnamese License Plate Recognition System
Main entry point
"""

import argparse
import sys
import os
from pathlib import Path

# Thêm src vào path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.preprocessing import ImagePreprocessor
from src.detection import PlateDetector
from src.recognition import CharacterSegmenter, CharacterRecognizer
from src.utils import load_image, save_results, get_image_files, Config


class LicensePlateRecognizer:
    """Class chính để nhận dạng biển số"""
    
    def __init__(self, model_path=None):
        """
        Khởi tạo hệ thống nhận dạng biển số
        
        Args:
            model_path: Đường dẫn đến thư mục chứa model (mặc định: models/)
        """
        Config.ensure_directories()
        
        if model_path is None:
            model_path = str(Config.MODEL_DIR)
        
        # Khởi tạo các module
        self.preprocessor = ImagePreprocessor()
        self.detector = PlateDetector()
        self.segmenter = CharacterSegmenter()
        self.recognizer = CharacterRecognizer(
            model_path=model_path,
            classifications_file=Config.CLASSIFICATIONS_FILE,
            flattened_images_file=Config.FLATTENED_IMAGES_FILE
        )
    
    def recognize(self, image_path):
        """
        Nhận dạng biển số trong ảnh
        
        Args:
            image_path: Đường dẫn đến file ảnh
            
        Returns:
            results: Danh sách biển số được nhận dạng [plate_text, ...]
        """
        # Load ảnh
        img = load_image(image_path)
        if img is None:
            print(f"Error: Cannot load image {image_path}")
            return []
        
        # Resize ảnh về kích thước chuẩn (1920x1080)
        img = self.detector.resize_image(img)
        
        # Preprocessing (ảnh đã được resize)
        img_grayscale, img_thresh = self.preprocessor.preprocess(img)
        
        # Detection
        plates, contours = self.detector.detect_plates(img, img_grayscale, img_thresh)
        
        if len(plates) == 0:
            return []
        
        # Recognition
        results = []
        for roi, roi_thresh in plates:
            try:
                # Segment characters
                characters, _ = self.segmenter.segment_characters(roi_thresh)
                
                if len(characters) == 0:
                    continue
                
                # Classify lines
                height, width = roi_thresh.shape[:2]
                first_line_chars, second_line_chars = self.segmenter.classify_lines(
                    characters, height
                )
                
                # Recognize
                plate_text = self.recognizer.recognize_plate(
                    first_line_chars, second_line_chars
                )
                
                if plate_text:
                    results.append(plate_text)
            
            except Exception as e:
                print(f"Error processing plate: {e}")
                continue
        
        return results
    
    def recognize_batch(self, image_paths):
        """
        Nhận dạng biển số từ nhiều ảnh
        
        Args:
            image_paths: Danh sách đường dẫn ảnh
            
        Returns:
            results: Danh sách kết quả [(image_path, [plate_texts]), ...]
        """
        results = []
        for image_path in image_paths:
            plate_texts = self.recognize(image_path)
            results.append((image_path, plate_texts))
        return results


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Vietnamese License Plate Recognition System'
    )
    parser.add_argument(
        'input',
        help='Đường dẫn đến file ảnh hoặc thư mục chứa ảnh'
    )
    parser.add_argument(
        '-o', '--output',
        default='results/recognized.txt',
        help='Đường dẫn file output (mặc định: results/recognized.txt)'
    )
    parser.add_argument(
        '-m', '--model',
        default=None,
        help='Đường dẫn đến thư mục chứa model (mặc định: models/)'
    )
    parser.add_argument(
        '--format',
        choices=['txt', 'json'],
        default='txt',
        help='Định dạng output (mặc định: txt)'
    )
    
    args = parser.parse_args()
    
    # Khởi tạo hệ thống
    print("Initializing License Plate Recognition System...")
    try:
        recognizer = LicensePlateRecognizer(model_path=args.model)
        print("System initialized successfully!")
    except Exception as e:
        print(f"Error initializing system: {e}")
        sys.exit(1)
    
    # Lấy danh sách ảnh
    input_path = Path(args.input)
    if input_path.is_file():
        image_paths = [str(input_path)]
    elif input_path.is_dir():
        image_paths = get_image_files(str(input_path))
    else:
        print(f"Error: {args.input} is not a valid file or directory")
        sys.exit(1)
    
    if len(image_paths) == 0:
        print(f"Error: No images found in {args.input}")
        sys.exit(1)
    
    print(f"Found {len(image_paths)} image(s) to process")
    
    # Nhận dạng
    results = []
    for i, image_path in enumerate(image_paths, 1):
        print(f"\n[{i}/{len(image_paths)}] Processing: {os.path.basename(image_path)}")
        plate_texts = recognizer.recognize(image_path)
        
        if plate_texts:
            plate_text = " | ".join(plate_texts)
            print(f"  Result: {plate_text}")
        else:
            plate_text = "NO_PLATE"
            print(f"  Result: {plate_text}")
        
        results.append((image_path, plate_text))
    
    # Lưu kết quả
    output_path = args.output
    save_results(results, output_path, format=args.format)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()

