"""
Character Recognition Module
Nhận dạng ký tự sử dụng KNN
"""

import cv2
import numpy as np
import os


class CharacterRecognizer:
    """Class nhận dạng ký tự sử dụng KNN"""
    
    # Tham số mặc định
    RESIZED_IMAGE_WIDTH = 20
    RESIZED_IMAGE_HEIGHT = 30
    K_NEIGHBORS = 3
    
    def __init__(self, 
                 model_path="models",
                 classifications_file="classifications.txt",
                 flattened_images_file="flattened_images.txt",
                 k_neighbors=3):
        """
        Khởi tạo CharacterRecognizer
        
        Args:
            model_path: Đường dẫn đến thư mục chứa model
            classifications_file: Tên file classifications
            flattened_images_file: Tên file flattened images
            k_neighbors: Số láng giềng gần nhất cho KNN
        """
        self.K_NEIGHBORS = k_neighbors
        self.k_nearest = None
        self.load_model(model_path, classifications_file, flattened_images_file)
    
    def load_model(self, model_path, classifications_file, flattened_images_file):
        """
        Tải model KNN
        
        Args:
            model_path: Đường dẫn đến thư mục chứa model
            classifications_file: Tên file classifications
            flattened_images_file: Tên file flattened images
        """
        class_path = os.path.join(model_path, classifications_file)
        flat_path = os.path.join(model_path, flattened_images_file)
        
        if not os.path.exists(class_path) or not os.path.exists(flat_path):
            raise FileNotFoundError(
                f"Model files not found: {class_path} or {flat_path}"
            )
        
        # Load classifications
        npa_classifications = np.loadtxt(class_path, np.float32)
        npa_flattened_images = np.loadtxt(flat_path, np.float32)
        
        # Reshape
        npa_classifications = npa_classifications.reshape((npa_classifications.size, 1))
        
        # Train KNN
        self.k_nearest = cv2.ml.KNearest_create()
        self.k_nearest.train(npa_flattened_images, cv2.ml.ROW_SAMPLE, npa_classifications)
    
    def normalize_character(self, char_img):
        """
        Chuẩn hóa kích thước ký tự
        
        Args:
            char_img: Ảnh ký tự
            
        Returns:
            normalized: Ảnh ký tự đã chuẩn hóa (20x30)
        """
        return cv2.resize(char_img, (self.RESIZED_IMAGE_WIDTH, self.RESIZED_IMAGE_HEIGHT))
    
    def recognize_character(self, char_img):
        """
        Nhận dạng một ký tự
        
        Args:
            char_img: Ảnh ký tự
            
        Returns:
            character: Ký tự được nhận dạng (string)
        """
        if self.k_nearest is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Chuẩn hóa
        normalized = self.normalize_character(char_img)
        
        # Flatten thành vector
        flattened = normalized.reshape((1, self.RESIZED_IMAGE_WIDTH * self.RESIZED_IMAGE_HEIGHT))
        flattened = np.float32(flattened)
        
        # Nhận dạng bằng KNN
        _, results, _, _ = self.k_nearest.findNearest(flattened, self.K_NEIGHBORS)
        
        # Chuyển đổi ASCII sang ký tự
        char_code = int(results[0][0])
        character = chr(char_code)
        
        return character
    
    def recognize_plate(self, first_line_chars, second_line_chars):
        """
        Nhận dạng toàn bộ biển số
        
        Args:
            first_line_chars: Danh sách ký tự hàng trên
            second_line_chars: Danh sách ký tự hàng dưới
            
        Returns:
            plate_text: Text biển số (format: "ABC123 - 456789" hoặc "ABC12345")
        """
        first_line = ""
        second_line = ""
        
        # Nhận dạng hàng trên
        for char in first_line_chars:
            _, _, _, _, char_img = char
            char_text = self.recognize_character(char_img)
            first_line += char_text
        
        # Nhận dạng hàng dưới
        for char in second_line_chars:
            _, _, _, _, char_img = char
            char_text = self.recognize_character(char_img)
            second_line += char_text
        
        # Format kết quả
        if second_line:
            return f"{first_line} - {second_line}"
        else:
            return first_line

