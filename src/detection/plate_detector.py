"""
License Plate Detection Module
Phát hiện và trích xuất biển số từ ảnh
"""

import cv2
import numpy as np
import math


class PlateDetector:
    """Class phát hiện biển số trong ảnh"""
    
    # Tham số mặc định
    CANNY_THRESHOLD_LOW = 250
    CANNY_THRESHOLD_HIGH = 255
    DILATION_KERNEL_SIZE = (3, 3)
    DILATION_ITERATIONS = 1
    APPROX_POLY_EPSILON_FACTOR = 0.06
    MAX_CONTOURS = 10
    TARGET_SIZE = (1920, 1080)
    PLATE_SCALE_FACTOR = 3.0
    
    def __init__(self,
                 canny_low=250,
                 canny_high=255,
                 dilation_iterations=1,
                 approx_epsilon_factor=0.06,
                 max_contours=10,
                 target_size=(1920, 1080)):
        """
        Khởi tạo PlateDetector
        
        Args:
            canny_low: Ngưỡng thấp cho Canny edge detection
            canny_high: Ngưỡng cao cho Canny edge detection
            dilation_iterations: Số lần lặp cho dilation
            approx_epsilon_factor: Hệ số epsilon cho polygon approximation
            max_contours: Số lượng contour tối đa để xử lý
            target_size: Kích thước chuẩn hóa ảnh (width, height)
        """
        self.CANNY_THRESHOLD_LOW = canny_low
        self.CANNY_THRESHOLD_HIGH = canny_high
        self.DILATION_ITERATIONS = dilation_iterations
        self.APPROX_POLY_EPSILON_FACTOR = approx_epsilon_factor
        self.MAX_CONTOURS = max_contours
        self.TARGET_SIZE = target_size
    
    def resize_image(self, img):
        """Resize ảnh về kích thước chuẩn"""
        return cv2.resize(img, self.TARGET_SIZE)
    
    def detect_edges(self, img_thresh):
        """
        Phát hiện cạnh bằng Canny edge detection
        
        Args:
            img_thresh: Ảnh nhị phân
            
        Returns:
            canny_image: Ảnh cạnh
        """
        return cv2.Canny(
            img_thresh,
            self.CANNY_THRESHOLD_LOW,
            self.CANNY_THRESHOLD_HIGH
        )
    
    def dilate_edges(self, canny_image):
        """
        Dilation để nối các cạnh bị đứt đoạn
        
        Args:
            canny_image: Ảnh cạnh
            
        Returns:
            dilated_image: Ảnh đã dilation
        """
        kernel = np.ones(self.DILATION_KERNEL_SIZE, np.uint8)
        return cv2.dilate(canny_image, kernel, iterations=self.DILATION_ITERATIONS)
    
    def find_plate_contours(self, dilated_image):
        """
        Tìm các contour có thể là biển số (hình tứ giác)
        
        Args:
            dilated_image: Ảnh đã dilation
            
        Returns:
            plate_contours: Danh sách contour có 4 đỉnh
        """
        contours, _ = cv2.findContours(
            dilated_image,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Sắp xếp theo diện tích, lấy top N
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:self.MAX_CONTOURS]
        
        plate_contours = []
        for contour in contours:
            # Tính chu vi
            peri = cv2.arcLength(contour, True)
            
            # Xấp xỉ đa giác
            approx = cv2.approxPolyDP(
                contour,
                self.APPROX_POLY_EPSILON_FACTOR * peri,
                True
            )
            
            # Chỉ lấy contour có 4 đỉnh (hình tứ giác)
            if len(approx) == 4:
                plate_contours.append(approx)
        
        return plate_contours
    
    def calculate_rotation_angle(self, contour):
        """
        Tính góc xoay của biển số
        
        Args:
            contour: Contour của biển số (4 đỉnh)
            
        Returns:
            angle: Góc xoay (độ)
        """
        # Lấy 4 đỉnh
        (x1, y1) = contour[0, 0]
        (x2, y2) = contour[1, 0]
        (x3, y3) = contour[2, 0]
        (x4, y4) = contour[3, 0]
        
        # Sắp xếp theo tọa độ y (giảm dần)
        points = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        points.sort(reverse=True, key=lambda p: p[1])
        
        # Lấy 2 điểm dưới cùng
        (x1, y1) = points[0]
        (x2, y2) = points[1]
        
        # Tính góc
        doi = abs(y1 - y2)
        ke = abs(x1 - x2)
        
        if ke == 0:
            return 0.0
        
        angle = math.atan(doi / ke) * (180.0 / math.pi)
        return angle
    
    def extract_plate_region(self, img, img_grayscale, img_thresh, contour):
        """
        Trích xuất vùng biển số từ ảnh
        
        Args:
            img: Ảnh gốc
            img_grayscale: Ảnh grayscale
            img_thresh: Ảnh nhị phân
            contour: Contour của biển số
            
        Returns:
            roi: Vùng biển số (ảnh màu)
            roi_thresh: Vùng biển số (ảnh nhị phân)
            angle: Góc xoay
        """
        # Tạo mask từ img_grayscale để tìm vùng
        mask = np.zeros(img_grayscale.shape, np.uint8)
        cv2.drawContours(mask, [contour], 0, 255, -1)
        
        # Tìm vùng
        (x, y) = np.where(mask == 255)
        if len(x) == 0 or len(y) == 0:
            return None, None, 0
        
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        
        # Crop từ ảnh gốc và ảnh nhị phân
        roi = img[topx:bottomx, topy:bottomy]
        roi_thresh = img_thresh[topx:bottomx, topy:bottomy]
        
        # Tính góc xoay
        angle = self.calculate_rotation_angle(contour)
        
        # Xoay ảnh
        pt_center = ((bottomx - topx) / 2, (bottomy - topy) / 2)
        
        # Lấy 2 điểm dưới cùng để xác định hướng xoay
        (x1, y1) = contour[0, 0]
        (x2, y2) = contour[1, 0]
        (x3, y3) = contour[2, 0]
        (x4, y4) = contour[3, 0]
        points = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        points.sort(reverse=True, key=lambda p: p[1])
        (x1, y1) = points[0]
        (x2, y2) = points[1]
        
        if x1 < x2:
            rotation_matrix = cv2.getRotationMatrix2D(pt_center, -angle, 1.0)
        else:
            rotation_matrix = cv2.getRotationMatrix2D(pt_center, angle, 1.0)
        
        roi = cv2.warpAffine(
            roi,
            rotation_matrix,
            (bottomy - topy, bottomx - topx)
        )
        roi_thresh = cv2.warpAffine(
            roi_thresh,
            rotation_matrix,
            (bottomy - topy, bottomx - topx)
        )
        
        # Phóng to
        roi = cv2.resize(roi, None, fx=self.PLATE_SCALE_FACTOR, fy=self.PLATE_SCALE_FACTOR)
        roi_thresh = cv2.resize(roi_thresh, None, fx=self.PLATE_SCALE_FACTOR, fy=self.PLATE_SCALE_FACTOR)
        
        return roi, roi_thresh, angle
    
    def detect_plates(self, img, img_grayscale, img_thresh):
        """
        Phát hiện tất cả biển số trong ảnh
        
        Args:
            img: Ảnh gốc (đã resize về target size)
            img_grayscale: Ảnh grayscale (đã resize về target size)
            img_thresh: Ảnh nhị phân (đã resize về target size)
            
        Returns:
            plates: Danh sách vùng biển số [(roi, roi_thresh), ...]
            contours: Danh sách contour tương ứng
        """
        # Phát hiện cạnh
        canny_image = self.detect_edges(img_thresh)
        
        # Dilation
        dilated_image = self.dilate_edges(canny_image)
        
        # Tìm contour
        plate_contours = self.find_plate_contours(dilated_image)
        
        # Trích xuất vùng biển số
        plates = []
        valid_contours = []
        
        # Lưu ảnh gốc để crop (tránh bị vẽ contour lên)
        img_original = img.copy()
        
        for contour in plate_contours:
            roi, roi_thresh, angle = self.extract_plate_region(
                img_original, img_grayscale, img_thresh, contour
            )
            if roi is not None and roi_thresh is not None:
                plates.append((roi, roi_thresh))
                valid_contours.append(contour)
        
        return plates, valid_contours

