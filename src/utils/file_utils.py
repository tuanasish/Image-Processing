"""
File utility functions
"""

import os
import cv2
from pathlib import Path


def load_image(image_path):
    """
    Load ảnh từ đường dẫn
    
    Args:
        image_path: Đường dẫn đến file ảnh
        
    Returns:
        img: Ảnh (numpy array) hoặc None nếu lỗi
    """
    if not os.path.exists(image_path):
        return None
    
    img = cv2.imread(image_path)
    return img


def save_results(results, output_path, format='txt'):
    """
    Lưu kết quả nhận dạng
    
    Args:
        results: Danh sách kết quả [(image_path, plate_text), ...]
        output_path: Đường dẫn file output
        format: Định dạng output ('txt' hoặc 'json')
    """
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    if format == 'txt':
        with open(output_path, 'w', encoding='utf-8') as f:
            for image_path, plate_text in results:
                image_name = os.path.basename(image_path)
                f.write(f"{image_name}\t{plate_text}\n")
    elif format == 'json':
        import json
        data = [
            {
                'image': os.path.basename(img_path),
                'plate': plate_text
            }
            for img_path, plate_text in results
        ]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def create_output_directory(output_dir):
    """
    Tạo thư mục output nếu chưa tồn tại
    
    Args:
        output_dir: Đường dẫn thư mục output
    """
    os.makedirs(output_dir, exist_ok=True)


def get_image_files(directory, extensions=None):
    """
    Lấy danh sách file ảnh trong thư mục
    
    Args:
        directory: Đường dẫn thư mục
        extensions: Danh sách extension (mặc định: ['.jpg', '.jpeg', '.png', '.bmp'])
        
    Returns:
        image_files: Danh sách đường dẫn file ảnh
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP']
    
    image_files = []
    if os.path.isdir(directory):
        for filename in os.listdir(directory):
            if any(filename.lower().endswith(ext.lower()) for ext in extensions):
                image_files.append(os.path.join(directory, filename))
    
    return sorted(image_files)

