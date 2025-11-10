"""
Character Segmentation Module
Phân đoạn ký tự từ ảnh biển số
"""

import cv2
import numpy as np


class CharacterSegmenter:
    """Class phân đoạn ký tự từ biển số"""
    
    # Tham số mặc định
    MIN_CHAR_AREA_RATIO = 0.01  # 1% diện tích biển số
    MAX_CHAR_AREA_RATIO = 0.09  # 9% diện tích biển số
    MIN_CHAR_RATIO = 0.25  # Tỷ lệ width/height tối thiểu
    MAX_CHAR_RATIO = 0.7   # Tỷ lệ width/height tối đa
    MORPHOLOGY_KERNEL_SIZE = (3, 3)
    LINE_DIVISION_FACTOR = 3  # Chia biển số thành 3 phần theo chiều dọc
    
    def __init__(self,
                 min_char_area_ratio=0.01,
                 max_char_area_ratio=0.09,
                 min_char_ratio=0.25,
                 max_char_ratio=0.7):
        """
        Khởi tạo CharacterSegmenter
        
        Args:
            min_char_area_ratio: Tỷ lệ diện tích ký tự tối thiểu so với biển số
            max_char_area_ratio: Tỷ lệ diện tích ký tự tối đa so với biển số
            min_char_ratio: Tỷ lệ width/height tối thiểu
            max_char_ratio: Tỷ lệ width/height tối đa
        """
        self.MIN_CHAR_AREA_RATIO = min_char_area_ratio
        self.MAX_CHAR_AREA_RATIO = max_char_area_ratio
        self.MIN_CHAR_RATIO = min_char_ratio
        self.MAX_CHAR_RATIO = max_char_ratio
    
    def segment_characters(self, roi_thresh):
        """
        Phân đoạn ký tự từ ảnh biển số nhị phân
        
        Args:
            roi_thresh: Ảnh biển số nhị phân
            
        Returns:
            characters: Danh sách ký tự [(x, y, w, h, img), ...]
            sorted_indices: Chỉ số ký tự đã sắp xếp
        """
        # Dilation để nối các phần của ký tự
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, self.MORPHOLOGY_KERNEL_SIZE)
        thre_mor = cv2.morphologyEx(roi_thresh, cv2.MORPH_DILATE, kernel)
        
        # Tìm contour
        contours, _ = cv2.findContours(thre_mor, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Tính diện tích biển số
        height, width = roi_thresh.shape[:2]
        roi_area = height * width
        
        # Lọc ký tự
        char_x_ind = {}
        char_x = []
        
        for idx, contour in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(contour)
            ratio_char = w / h if h != 0 else 0
            char_area = w * h
            
            # Kiểm tra điều kiện
            area_ok = (self.MIN_CHAR_AREA_RATIO * roi_area < char_area < 
                      self.MAX_CHAR_AREA_RATIO * roi_area)
            ratio_ok = (self.MIN_CHAR_RATIO < ratio_char < self.MAX_CHAR_RATIO)
            
            if area_ok and ratio_ok:
                # Xử lý trùng lặp tọa độ x
                original_x = x
                while x in char_x:
                    x += 1
                
                char_x.append(x)
                char_x_ind[x] = idx
        
        if len(char_x) == 0:
            return [], []
        
        # Sắp xếp theo tọa độ x
        char_x_sorted = sorted(char_x)
        
        # Trích xuất ký tự
        characters = []
        for x in char_x_sorted:
            idx = char_x_ind[x]
            (x, y, w, h) = cv2.boundingRect(contours[idx])
            char_img = thre_mor[y:y + h, x:x + w]
            characters.append((x, y, w, h, char_img))
        
        return characters, char_x_sorted
    
    def classify_lines(self, characters, plate_height):
        """
        Phân loại ký tự thành hàng trên và hàng dưới
        
        Args:
            characters: Danh sách ký tự [(x, y, w, h, img), ...]
            plate_height: Chiều cao biển số
            
        Returns:
            first_line_chars: Ký tự hàng trên
            second_line_chars: Ký tự hàng dưới
        """
        first_line_chars = []
        second_line_chars = []
        
        threshold = plate_height / self.LINE_DIVISION_FACTOR
        
        for char in characters:
            x, y, w, h, img = char
            if y < threshold:
                first_line_chars.append(char)
            else:
                second_line_chars.append(char)
        
        return first_line_chars, second_line_chars

