"""
Image Preprocessing Module
Xử lý ảnh: chuyển đổi màu, tăng độ tương phản, làm mịn, nhị phân hóa
"""

import cv2
import numpy as np


class ImagePreprocessor:
    """Class xử lý ảnh trước khi nhận dạng biển số"""
    
    # Tham số mặc định
    GAUSSIAN_SMOOTH_FILTER_SIZE = (5, 5)
    ADAPTIVE_THRESH_BLOCK_SIZE = 19
    ADAPTIVE_THRESH_WEIGHT = 9
    MORPHOLOGY_ITERATIONS = 10
    MORPHOLOGY_KERNEL_SIZE = (3, 3)
    
    def __init__(self, 
                 gaussian_kernel_size=(5, 5),
                 adaptive_block_size=19,
                 adaptive_weight=9,
                 morphology_iterations=10):
        """
        Khởi tạo ImagePreprocessor
        
        Args:
            gaussian_kernel_size: Kích thước kernel Gaussian blur
            adaptive_block_size: Kích thước block cho adaptive threshold
            adaptive_weight: Trọng số cho adaptive threshold
            morphology_iterations: Số lần lặp cho phép toán hình thái học
        """
        self.GAUSSIAN_SMOOTH_FILTER_SIZE = gaussian_kernel_size
        self.ADAPTIVE_THRESH_BLOCK_SIZE = adaptive_block_size
        self.ADAPTIVE_THRESH_WEIGHT = adaptive_weight
        self.MORPHOLOGY_ITERATIONS = morphology_iterations
    
    def extract_value(self, img_original):
        """
        Chuyển đổi ảnh BGR sang HSV và trích xuất kênh Value (độ sáng)
        
        Args:
            img_original: Ảnh gốc (BGR)
            
        Returns:
            img_value: Ảnh grayscale từ kênh Value của HSV
        """
        img_hsv = cv2.cvtColor(img_original, cv2.COLOR_BGR2HSV)
        _, _, img_value = cv2.split(img_hsv)
        return img_value
    
    def maximize_contrast(self, img_grayscale):
        """
        Tăng độ tương phản bằng Top Hat và Black Hat morphology
        
        Args:
            img_grayscale: Ảnh grayscale
            
        Returns:
            img_enhanced: Ảnh đã tăng độ tương phản
        """
        structuring_element = cv2.getStructuringElement(
            cv2.MORPH_RECT, 
            self.MORPHOLOGY_KERNEL_SIZE
        )
        
        # Top Hat: nổi bật chi tiết sáng trong nền tối
        img_top_hat = cv2.morphologyEx(
            img_grayscale, 
            cv2.MORPH_TOPHAT, 
            structuring_element, 
            iterations=self.MORPHOLOGY_ITERATIONS
        )
        
        # Black Hat: nổi bật chi tiết tối trong nền sáng
        img_black_hat = cv2.morphologyEx(
            img_grayscale, 
            cv2.MORPH_BLACKHAT, 
            structuring_element, 
            iterations=self.MORPHOLOGY_ITERATIONS
        )
        
        # Kết hợp: img + TopHat - BlackHat
        img_plus_top_hat = cv2.add(img_grayscale, img_top_hat)
        img_enhanced = cv2.subtract(img_plus_top_hat, img_black_hat)
        
        return img_enhanced
    
    def preprocess(self, img_original):
        """
        Xử lý ảnh đầy đủ: chuyển đổi màu, tăng độ tương phản, 
        làm mịn, nhị phân hóa
        
        Args:
            img_original: Ảnh gốc (BGR)
            
        Returns:
            img_grayscale: Ảnh grayscale
            img_thresh: Ảnh nhị phân
        """
        # Bước 1: Chuyển đổi sang HSV và trích xuất Value
        img_grayscale = self.extract_value(img_original)
        
        # Bước 2: Tăng độ tương phản
        img_max_contrast = self.maximize_contrast(img_grayscale)
        
        # Bước 3: Làm mịn bằng Gaussian blur
        img_blurred = cv2.GaussianBlur(
            img_max_contrast, 
            self.GAUSSIAN_SMOOTH_FILTER_SIZE, 
            0
        )
        
        # Bước 4: Nhị phân hóa bằng Adaptive Threshold
        img_thresh = cv2.adaptiveThreshold(
            img_blurred,
            255.0,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            self.ADAPTIVE_THRESH_BLOCK_SIZE,
            self.ADAPTIVE_THRESH_WEIGHT
        )
        
        return img_grayscale, img_thresh

