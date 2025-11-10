# Hướng Dẫn Sử Dụng

## Cài Đặt

### 1. Cài đặt Python

Đảm bảo đã cài đặt Python 3.7 trở lên:

```bash
python --version
```

### 2. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### 3. Chuẩn Bị Model

Đảm bảo có các file model trong thư mục `models/`:
- `classifications.txt`
- `flattened_images.txt`

## Sử Dụng Cơ Bản

### Nhận Dạng Một Ảnh

```bash
python main.py data/test_images/image.jpg
```

### Nhận Dạng Nhiều Ảnh

```bash
python main.py data/test_images/
```

### Lưu Kết Quả

```bash
python main.py data/test_images/image.jpg -o results/output.txt
```

### Lưu Kết Quả Dạng JSON

```bash
python main.py data/test_images/image.jpg -o results/output.json --format json
```

## Sử Dụng Trong Python Code

### Ví Dụ Cơ Bản

```python
from main import LicensePlateRecognizer

# Khởi tạo hệ thống
recognizer = LicensePlateRecognizer()

# Nhận dạng một ảnh
results = recognizer.recognize("path/to/image.jpg")
print(results)  # ['ABC123 - 456789']
```

### Nhận Dạng Nhiều Ảnh

```python
from main import LicensePlateRecognizer
from src.utils import get_image_files

# Khởi tạo hệ thống
recognizer = LicensePlateRecognizer()

# Lấy danh sách ảnh
image_paths = get_image_files("data/test_images/")

# Nhận dạng
results = recognizer.recognize_batch(image_paths)

# In kết quả
for image_path, plate_texts in results:
    print(f"{image_path}: {plate_texts}")
```

## Tùy Chỉnh Tham Số

### Thay Đổi Tham Số Preprocessing

```python
from src.preprocessing import ImagePreprocessor

preprocessor = ImagePreprocessor(
    gaussian_kernel_size=(7, 7),
    adaptive_block_size=21,
    adaptive_weight=10
)
```

### Thay Đổi Tham Số Detection

```python
from src.detection import PlateDetector

detector = PlateDetector(
    canny_low=200,
    canny_high=255,
    max_contours=15
)
```

### Thay Đổi Tham Số Segmentation

```python
from src.recognition import CharacterSegmenter

segmenter = CharacterSegmenter(
    min_char_area_ratio=0.015,
    max_char_area_ratio=0.08,
    min_char_ratio=0.2,
    max_char_ratio=0.75
)
```

## Xử Lý Lỗi

### Lỗi Model Không Tìm Thấy

Nếu gặp lỗi "Model files not found":
1. Kiểm tra thư mục `models/` có tồn tại không
2. Kiểm tra các file `classifications.txt` và `flattened_images.txt` có trong thư mục `models/` không
3. Nếu chưa có, cần train model trước

### Lỗi Không Đọc Được Ảnh

Nếu gặp lỗi "Cannot load image":
1. Kiểm tra đường dẫn ảnh có đúng không
2. Kiểm tra định dạng ảnh có được hỗ trợ không (JPG, PNG, BMP)
3. Kiểm tra quyền truy cập file

### Kết Quả Không Chính Xác

Nếu kết quả nhận dạng không chính xác:
1. Kiểm tra chất lượng ảnh (độ phân giải, ánh sáng)
2. Điều chỉnh tham số detection và segmentation
3. Đảm bảo ảnh có biển số rõ ràng, không bị mờ

## Tips

1. **Chất lượng ảnh**: Ảnh có độ phân giải cao, ánh sáng đều sẽ cho kết quả tốt hơn
2. **Góc chụp**: Ảnh chụp thẳng, không nghiêng quá nhiều sẽ nhận dạng tốt hơn
3. **Độ tương phản**: Biển số có độ tương phản cao với nền sẽ dễ phát hiện hơn
4. **Kích thước biển số**: Biển số chiếm khoảng 10-30% diện tích ảnh sẽ cho kết quả tốt nhất

## Troubleshooting

### Vấn đề: Không phát hiện được biển số

**Giải pháp:**
- Kiểm tra ảnh có biển số rõ ràng không
- Điều chỉnh tham số Canny edge detection
- Tăng số lượng contour tối đa (`max_contours`)

### Vấn đề: Nhận dạng sai ký tự

**Giải pháp:**
- Kiểm tra chất lượng ảnh biển số
- Điều chỉnh tham số segmentation
- Retrain model với nhiều mẫu hơn

### Vấn đề: Tốc độ xử lý chậm

**Giải pháp:**
- Giảm kích thước ảnh đầu vào
- Giảm số lượng contour tối đa
- Sử dụng ảnh có độ phân giải thấp hơn

## Liên Hệ

Nếu gặp vấn đề, vui lòng tạo issue trên repository hoặc liên hệ trực tiếp.

