# Web UI - Nhận Dạng Biển Số Xe

## Mô Tả

Giao diện web đẹp mắt để demo hệ thống nhận dạng biển số xe sử dụng Flask.

## Cài Đặt

### 1. Cài Đặt Dependencies

```bash
pip install -r ../requirements.txt
```

### 2. Đảm Bảo Có Model

Đảm bảo có các file model trong thư mục `../models/`:
- `classifications.txt`
- `flattened_images.txt`

## Chạy Web UI

### Cách 1: Chạy Trực Tiếp

```bash
cd web
python app.py
```

### Cách 2: Sử Dụng Flask CLI

```bash
cd web
export FLASK_APP=app.py
flask run
```

### Cách 3: Chạy Với Python Module

```bash
python -m web.app
```

## Truy Cập

Sau khi chạy, mở trình duyệt và truy cập:

```
http://127.0.0.0.1:5000
```

## Tính Năng

- ✅ Upload ảnh bằng cách kéo thả hoặc chọn file
- ✅ Nhận dạng biển số tự động
- ✅ Hiển thị ảnh gốc với vùng phát hiện được khoanh vùng
- ✅ Hiển thị từng biển số đã được cắt và nhận dạng
- ✅ Hiển thị kết quả text của biển số
- ✅ Giao diện đẹp, responsive, dễ sử dụng
- ✅ Xử lý lỗi đầy đủ

## API Endpoints

### POST /api/recognize

Nhận dạng biển số từ ảnh upload.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image file)

**Response:**
```json
{
    "success": true,
    "results": ["ABC123 - 456789"],
    "result_text": "ABC123 - 456789",
    "detected_image": "base64_encoded_image",
    "plate_images": ["base64_encoded_image"],
    "count": 1
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
    "status": "ok",
    "message": "System is running"
}
```

## Cấu Trúc

```
web/
├── app.py                 # Flask application
├── templates/            # HTML templates
│   └── index.html       # Main page
├── static/              # Static files
│   ├── css/            # Stylesheets
│   │   └── style.css
│   └── js/             # JavaScript (nếu có)
└── uploads/            # Uploaded files (temporary)
```

## Tùy Chỉnh

### Thay Đổi Port

Sửa trong `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Thay đổi port
```

### Thay Đổi Kích Thước Upload

Sửa trong `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

## Troubleshooting

### Lỗi: Model files not found

**Giải pháp:**
- Kiểm tra file model có trong `../models/` không
- Kiểm tra đường dẫn trong `app.py`

### Lỗi: Port đã được sử dụng

**Giải pháp:**
- Thay đổi port trong `app.py`
- Hoặc dừng ứng dụng đang chạy trên port đó

### Lỗi: Cannot load image

**Giải pháp:**
- Kiểm tra định dạng ảnh (JPG, PNG, JPEG)
- Kiểm tra kích thước file (tối đa 16MB)

## Lưu Ý

- Web UI sử dụng các module từ `src/`
- Đảm bảo đã cài đặt đầy đủ dependencies
- Model KNN phải có sẵn trước khi chạy

## Phát Triển

### Thêm Tính Năng Mới

1. Thêm route mới trong `app.py`
2. Thêm template HTML nếu cần
3. Thêm CSS/JS nếu cần
4. Test và kiểm tra

### Cải Thiện UI

- Sửa file `templates/index.html` để thay đổi giao diện
- Sửa file `static/css/style.css` để thay đổi style
- Thêm JavaScript trong template hoặc file riêng

