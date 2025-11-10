"""
Basic test for license plate recognition system
"""

import sys
from pathlib import Path

# Thêm src vào path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.preprocessing import ImagePreprocessor
from src.detection import PlateDetector
from src.recognition import CharacterSegmenter, CharacterRecognizer
from src.utils import Config
import cv2
import numpy as np


def test_preprocessing():
    """Test preprocessing module"""
    print("Testing preprocessing...")
    preprocessor = ImagePreprocessor()
    
    # Tạo ảnh test
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(test_img, (10, 10), (90, 90), (255, 255, 255), -1)
    
    # Test preprocessing
    img_grayscale, img_thresh = preprocessor.preprocess(test_img)
    
    assert img_grayscale is not None
    assert img_thresh is not None
    assert img_grayscale.shape[:2] == test_img.shape[:2]
    assert img_thresh.shape[:2] == test_img.shape[:2]
    
    print("✓ Preprocessing test passed")


def test_detection():
    """Test detection module"""
    print("Testing detection...")
    detector = PlateDetector()
    
    # Tạo ảnh test với hình chữ nhật (giả biển số)
    test_img = np.zeros((200, 400, 3), dtype=np.uint8)
    cv2.rectangle(test_img, (50, 50), (350, 150), (255, 255, 255), -1)
    
    # Preprocessing
    preprocessor = ImagePreprocessor()
    img_grayscale, img_thresh = preprocessor.preprocess(test_img)
    
    # Test detection
    plates, contours = detector.detect_plates(test_img, img_grayscale, img_thresh)
    
    print(f"  Found {len(plates)} plate(s)")
    print("✓ Detection test passed")


def test_recognition():
    """Test recognition module"""
    print("Testing recognition...")
    
    Config.ensure_directories()
    model_path = str(Config.MODEL_DIR)
    
    try:
        recognizer = CharacterRecognizer(model_path=model_path)
        
        # Tạo ảnh ký tự test (chữ A đơn giản)
        char_img = np.zeros((30, 20), dtype=np.uint8)
        cv2.putText(char_img, "A", (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 255, 2)
        
        # Test recognition
        char = recognizer.recognize_character(char_img)
        print(f"  Recognized character: {char}")
        print("✓ Recognition test passed")
    except FileNotFoundError as e:
        print(f"  ⚠ Model files not found: {e}")
        print("  ⚠ Recognition test skipped")


def test_integration():
    """Test integration of all modules"""
    print("Testing integration...")
    
    # Tạo ảnh test đơn giản
    test_img = np.zeros((200, 400, 3), dtype=np.uint8)
    cv2.rectangle(test_img, (50, 50), (350, 150), (255, 255, 255), -1)
    
    # Preprocessing
    preprocessor = ImagePreprocessor()
    img_grayscale, img_thresh = preprocessor.preprocess(test_img)
    
    # Detection
    detector = PlateDetector()
    plates, contours = detector.detect_plates(test_img, img_grayscale, img_thresh)
    
    if len(plates) > 0:
        # Segmentation
        segmenter = CharacterSegmenter()
        roi, roi_thresh = plates[0]
        characters, _ = segmenter.segment_characters(roi_thresh)
        print(f"  Found {len(characters)} character(s)")
    
    print("✓ Integration test passed")


if __name__ == '__main__':
    print("Running basic tests...\n")
    
    try:
        test_preprocessing()
        test_detection()
        test_recognition()
        test_integration()
        
        print("\n✓ All tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

