"""
Configuration file
"""

import os
from pathlib import Path


class Config:
    """Class chứa các cấu hình của hệ thống"""
    
    # Đường dẫn
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    MODEL_DIR = BASE_DIR / "models"
    DATA_DIR = BASE_DIR / "data"
    RESULTS_DIR = BASE_DIR / "results"
    
    # Model files
    CLASSIFICATIONS_FILE = "classifications.txt"
    FLATTENED_IMAGES_FILE = "flattened_images.txt"
    
    # Image processing parameters
    TARGET_IMAGE_SIZE = (1920, 1080)
    RESIZED_CHAR_WIDTH = 20
    RESIZED_CHAR_HEIGHT = 30
    
    # Detection parameters
    CANNY_LOW = 250
    CANNY_HIGH = 255
    DILATION_ITERATIONS = 1
    APPROX_EPSILON_FACTOR = 0.06
    MAX_CONTOURS = 10
    
    # Character segmentation parameters (giống Test_all_images.py)
    MIN_CHAR_AREA_RATIO = 0.01  # 1% diện tích biển số
    MAX_CHAR_AREA_RATIO = 0.09  # 9% diện tích biển số
    MIN_CHAR_RATIO = 0.25       # Tỷ lệ width/height tối thiểu
    MAX_CHAR_RATIO = 0.7        # Tỷ lệ width/height tối đa
    
    # Recognition parameters
    K_NEIGHBORS = 3
    
    # Preprocessing parameters
    GAUSSIAN_KERNEL_SIZE = (5, 5)
    ADAPTIVE_BLOCK_SIZE = 19
    ADAPTIVE_WEIGHT = 9
    MORPHOLOGY_ITERATIONS = 10
    
    @classmethod
    def get_model_path(cls, filename):
        """Lấy đường dẫn đầy đủ đến file model"""
        return cls.MODEL_DIR / filename
    
    @classmethod
    def get_data_path(cls, *paths):
        """Lấy đường dẫn đầy đủ đến thư mục data"""
        return cls.DATA_DIR / Path(*paths)
    
    @classmethod
    def get_results_path(cls, *paths):
        """Lấy đường dẫn đầy đủ đến thư mục results"""
        return cls.RESULTS_DIR / Path(*paths)
    
    @classmethod
    def ensure_directories(cls):
        """Tạo các thư mục cần thiết nếu chưa tồn tại"""
        cls.MODEL_DIR.mkdir(exist_ok=True)
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.RESULTS_DIR.mkdir(exist_ok=True)

