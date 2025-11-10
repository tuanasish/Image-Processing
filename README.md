# Hệ Thống Nhận Dạng Biển Số Xe Việt Nam

## Mô Tả

Hệ thống nhận dạng biển số xe Việt Nam sử dụng OpenCV và thuật toán K-Nearest Neighbors (KNN). Hệ thống hỗ trợ cả biển số 1 hàng và 2 hàng.

## Tính Năng

- ✅ Phát hiện biển số tự động từ ảnh
- ✅ Nhận dạng ký tự trên biển số
- ✅ Hỗ trợ biển số 1 hàng và 2 hàng
- ✅ Xử lý ảnh nghiêng (tự động xoay)
- ✅ Xử lý hàng loạt ảnh
- ✅ **Web UI đẹp mắt, dễ sử dụng**
- ✅ Code được tổ chức rõ ràng, dễ bảo trì

## Cấu Trúc Dự Án

```
VIETNAMESE_LICENSE_PLATE_CLEAN/
├── src/                          # Source code
│   ├── preprocessing/            # Module xử lý ảnh
│   │   ├── __init__.py
│   │   └── image_preprocessor.py
│   ├── detection/                # Module phát hiện biển số
│   │   ├── __init__.py
│   │   └── plate_detector.py
│   ├── recognition/              # Module nhận dạng ký tự
│   │   ├── __init__.py
│   │   ├── character_segmenter.py
│   │   └── character_recognizer.py
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── file_utils.py
│       └── config.py
├── models/                       # Model KNN
│   ├── classifications.txt
│   └── flattened_images.txt
├── data/                         # Dữ liệu
│   ├── test_images/              # Ảnh test
│   └── training/                 # Ảnh training
├── results/                      # Kết quả
├── tests/                        # Test scripts
├── docs/                         # Tài liệu
├── web/                          # Web UI
│   ├── app.py                   # Flask application
│   ├── templates/               # HTML templates
│   └── static/                  # CSS, JS
├── main.py                       # File chính (CLI)
├── requirements.txt              # Dependencies
└── README.md                     # File này
```

## Cài Đặt

### Yêu Cầu

- Python 3.7+
- OpenCV 4.5+
- NumPy 1.19+

### Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### Chuẩn Bị Model

Đảm bảo có các file model trong thư mục `models/`:
- `classifications.txt`
- `flattened_images.txt`

Nếu chưa có, bạn cần train model trước (xem phần Training Model).

## Sử Dụng

### Web UI (Khuyến Nghị)

Chạy Web UI để sử dụng giao diện đẹp mắt:

**Windows:**
```bash
run_web_ui.bat
```

**Linux/Mac:**
```bash
chmod +x run_web_ui.sh
./run_web_ui.sh
```

**Hoặc chạy trực tiếp:**
```bash
cd web
python app.py
```

Sau đó mở trình duyệt: **http://127.0.0.1:5000**

### Command Line Interface (CLI)

#### Nhận Dạng Một Ảnh

```bash
python main.py path/to/image.jpg
```

#### Nhận Dạng Nhiều Ảnh

```bash
python main.py path/to/images/
```

#### Lưu Kết Quả Vào File

```bash
python main.py path/to/image.jpg -o results/output.txt
```

#### Lưu Kết Quả Dạng JSON

```bash
python main.py path/to/image.jpg -o results/output.json --format json
```

#### Sử Dụng Model Tùy Chỉnh

```bash
python main.py path/to/image.jpg -m path/to/model/
```

## Các Tham Số

### Preprocessing
- `GAUSSIAN_KERNEL_SIZE`: Kích thước kernel Gaussian blur (mặc định: (5, 5))
- `ADAPTIVE_BLOCK_SIZE`: Kích thước block cho adaptive threshold (mặc định: 19)
- `ADAPTIVE_WEIGHT`: Trọng số cho adaptive threshold (mặc định: 9)
- `MORPHOLOGY_ITERATIONS`: Số lần lặp cho morphology (mặc định: 10)

### Detection
- `CANNY_LOW`: Ngưỡng thấp cho Canny edge (mặc định: 250)
- `CANNY_HIGH`: Ngưỡng cao cho Canny edge (mặc định: 255)
- `MAX_CONTOURS`: Số lượng contour tối đa (mặc định: 10)

### Character Segmentation
- `MIN_CHAR_AREA_RATIO`: Tỷ lệ diện tích ký tự tối thiểu (mặc định: 0.01)
- `MAX_CHAR_AREA_RATIO`: Tỷ lệ diện tích ký tự tối đa (mặc định: 0.09)
- `MIN_CHAR_RATIO`: Tỷ lệ width/height tối thiểu (mặc định: 0.25)
- `MAX_CHAR_RATIO`: Tỷ lệ width/height tối đa (mặc định: 0.7)

### Recognition
- `K_NEIGHBORS`: Số láng giềng gần nhất cho KNN (mặc định: 3)

## Phương Pháp Xử Lý Ảnh

Hệ thống sử dụng các phương pháp sau:

1. **Chuyển đổi màu**: BGR → HSV (trích xuất kênh Value)
2. **Tăng độ tương phản**: Top Hat và Black Hat morphology
3. **Làm mịn ảnh**: Gaussian blur
4. **Nhị phân hóa**: Adaptive threshold
5. **Phát hiện cạnh**: Canny edge detection
6. **Dilation**: Nối các cạnh bị đứt đoạn
7. **Contour detection**: Tìm contour hình tứ giác
8. **Xoay ảnh**: Affine transformation
9. **Phân đoạn ký tự**: Contour-based segmentation
10. **Nhận dạng ký tự**: K-Nearest Neighbors (KNN)

Xem thêm chi tiết trong file `docs/PHUONG_PHAP_XU_LY_ANH.md`

## Web UI

### Tính Năng Web UI

- ✅ Upload ảnh bằng cách kéo thả hoặc chọn file
- ✅ Nhận dạng biển số tự động
- ✅ Hiển thị ảnh gốc với vùng phát hiện được khoanh vùng
- ✅ Hiển thị từng biển số đã được cắt và nhận dạng
- ✅ Hiển thị kết quả text của biển số
- ✅ Giao diện đẹp, responsive, dễ sử dụng

### Chạy Web UI

Xem hướng dẫn chi tiết trong file `web/README.md`

## Training Model

Để train model mới:

1. Chuẩn bị ảnh training chứa ký tự (file `training_chars.png`)
2. Chạy script training:

```bash
python scripts/train_model.py
```

Script sẽ tạo ra các file:
- `models/classifications.txt`
- `models/flattened_images.txt`

## Kết Quả

Hệ thống đạt được:
- **Tỷ lệ phát hiện biển số**: ~95%
- **Tỷ lệ nhận dạng chính xác**: ~33-48% (tùy loại biển số)

## Hạn Chế

- Kém với ảnh có ánh sáng yếu, phản chiếu mạnh
- Nhận dạng kém với biển số bị mờ, nhiễu
- Có thể nhầm lẫn giữa một số ký tự (1↔7, G↔D, 6↔0, B↔8)

## Phát Triển

### Thêm Module Mới

1. Tạo file trong thư mục `src/` tương ứng
2. Thêm `__init__.py` để export class/function
3. Import và sử dụng trong `main.py`

### Test

```bash
python -m pytest tests/
```

## Tác Giả

Hệ thống được phát triển dựa trên các phương pháp xử lý ảnh và machine learning.

## License

Xem file LICENSE để biết thêm chi tiết.

## Tài Liệu Tham Khảo

- OpenCV Documentation: https://docs.opencv.org/
- K-Nearest Neighbors: https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm
- Image Processing: https://en.wikipedia.org/wiki/Digital_image_processing

