# Các Phương Pháp Xử Lý Ảnh Trong Dự Án

## Tổng quan

Dự án sử dụng nhiều kỹ thuật xử lý ảnh từ cơ bản đến nâng cao để nhận dạng biển số xe Việt Nam. Dưới đây là danh sách chi tiết các phương pháp được áp dụng:

---

## 1. GIAI ĐOẠN TIỀN XỬ LÝ (Preprocessing)

### 1.1. Chuyển đổi không gian màu (Color Space Conversion)
- **Phương pháp**: Chuyển từ BGR sang HSV
- **Hàm OpenCV**: `cv2.cvtColor(img, cv2.COLOR_BGR2HSV)`
- **Mục đích**: 
  - Trích xuất kênh Value (độ sáng) để loại bỏ ảnh hưởng của màu sắc
  - HSV tốt hơn RGB trong việc xử lý với ánh sáng thay đổi
- **Code**: `Preprocess.py` - hàm `extractValue()`

### 1.2. Tăng độ tương phản (Contrast Enhancement)
- **Phương pháp**: Morphological Operations - Top Hat và Black Hat
- **Hàm OpenCV**: 
  - `cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel)`
  - `cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel)`
- **Mục đích**:
  - Top Hat: Nổi bật chi tiết sáng trong nền tối
  - Black Hat: Nổi bật chi tiết tối trong nền sáng
  - Công thức: `img + TopHat - BlackHat`
- **Tham số**: Kernel (3x3), iterations = 10
- **Code**: `Preprocess.py` - hàm `maximizeContrast()`

### 1.3. Làm mịn ảnh (Image Smoothing)
- **Phương pháp**: Gaussian Blur
- **Hàm OpenCV**: `cv2.GaussianBlur(img, (5, 5), 0)`
- **Mục đích**:
  - Giảm nhiễu (noise reduction)
  - Làm mịn ảnh trước khi xử lý nhị phân
  - Tăng tốc độ xử lý
- **Tham số**: Kernel size (5x5), Sigma = 0
- **Code**: `Preprocess.py` - hàm `preprocess()`

### 1.4. Nhị phân hóa ảnh (Image Binarization)
- **Phương pháp**: Adaptive Threshold
- **Hàm OpenCV**: `cv2.adaptiveThreshold()`
- **Loại**: `ADAPTIVE_THRESH_GAUSSIAN_C`
- **Mục đích**:
  - Chuyển ảnh xám thành ảnh nhị phân (trắng/đen)
  - Adaptive threshold tự động điều chỉnh ngưỡng theo từng vùng
  - Phù hợp với ảnh có ánh sáng không đồng đều
- **Tham số**: 
  - Block size: 19
  - Weight: 9
  - Type: `THRESH_BINARY_INV` (đảo ngược: foreground trắng, background đen)
- **Code**: `Preprocess.py` - hàm `preprocess()`

---

## 2. GIAI ĐOẠN PHÁT HIỆN BIỂN SỐ (License Plate Detection)

### 2.1. Phát hiện cạnh (Edge Detection)
- **Phương pháp**: Canny Edge Detection
- **Hàm OpenCV**: `cv2.Canny(img, 250, 255)`
- **Mục đích**:
  - Phát hiện các cạnh trong ảnh nhị phân
  - Tìm ranh giới của biển số
- **Tham số**: 
  - Low threshold: 250
  - High threshold: 255
- **Code**: `Test_all_images.py`, `run_image.py`

### 2.2. Dilation (Giãn nở)
- **Phương pháp**: Morphological Dilation
- **Hàm OpenCV**: `cv2.dilate(img, kernel, iterations=1)`
- **Mục đích**:
  - Nối các cạnh bị đứt đoạn
  - Làm dày các đường cạnh
  - Tạo contour liên tục cho biển số
- **Tham số**: Kernel (3x3), iterations = 1
- **Code**: `Test_all_images.py`, `run_image.py`

### 2.3. Tìm Contour (Contour Detection)
- **Phương pháp**: Contour Finding
- **Hàm OpenCV**: `cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)`
- **Mục đích**:
  - Tìm tất cả các đường viền trong ảnh
  - Lọc và chọn contour có hình dạng giống biển số
- **Tham số**:
  - Mode: `RETR_TREE` (lấy tất cả contours và hierarchy)
  - Method: `CHAIN_APPROX_SIMPLE` (nén contour, chỉ giữ điểm đầu cuối)
- **Code**: `Test_all_images.py`, `run_image.py`

### 2.4. Xấp xỉ đa giác (Polygon Approximation)
- **Phương pháp**: Douglas-Peucker Algorithm
- **Hàm OpenCV**: `cv2.approxPolyDP(contour, 0.06 * peri, True)`
- **Mục đích**:
  - Đơn giản hóa contour thành đa giác
  - Lọc contour có 4 đỉnh (hình chữ nhật/tứ giác) - hình dạng biển số
- **Tham số**: 
  - Epsilon: 0.06 * chu vi (6% chu vi)
  - Closed: True
- **Code**: `Test_all_images.py`, `run_image.py`

### 2.5. Lọc Contour (Contour Filtering)
- **Phương pháp**: Area-based và Ratio-based Filtering
- **Mục đích**:
  - Sắp xếp contours theo diện tích (lớn nhất trước)
  - Lấy top 10 contours lớn nhất
  - Lọc contour có 4 đỉnh (hình tứ giác)
- **Code**: `Test_all_images.py`, `run_image.py`

### 2.6. Tạo Mask và Crop (Masking & Cropping)
- **Phương pháp**: Binary Mask
- **Hàm OpenCV**: 
  - `cv2.drawContours(mask, [contour], 0, 255, -1)`
  - `np.where(mask == 255)`
- **Mục đích**:
  - Tạo mask để tách biển số khỏi nền
  - Crop vùng biển số từ ảnh gốc
- **Code**: `Test_all_images.py`, `run_image.py`

---

## 3. GIAI ĐOẠN XỬ LÝ BIỂN SỐ (Plate Processing)

### 3.1. Tính toán góc xoay (Rotation Angle Calculation)
- **Phương pháp**: Geometric Calculation
- **Công thức**: `angle = atan(abs(y1 - y2) / abs(x1 - x2)) * (180 / π)`
- **Mục đích**:
  - Tính góc nghiêng của biển số
  - Sắp xếp 4 đỉnh theo tọa độ y, lấy 2 điểm dưới cùng
  - Tính góc dựa trên 2 điểm này
- **Code**: `Test_all_images.py`, `run_image.py`

### 3.2. Xoay ảnh (Image Rotation)
- **Phương pháp**: Affine Transformation
- **Hàm OpenCV**: 
  - `cv2.getRotationMatrix2D(center, angle, scale)`
  - `cv2.warpAffine(img, matrix, size)`
- **Mục đích**:
  - Xoay biển số về góc thẳng (0 độ)
  - Chuẩn hóa hướng biển số để nhận dạng tốt hơn
- **Tham số**: 
  - Center: Tâm của biển số
  - Angle: Góc xoay (có thể âm)
  - Scale: 1.0
- **Code**: `Test_all_images.py`, `run_image.py`

### 3.3. Resize ảnh (Image Resizing)
- **Phương pháp**: Scale Transformation
- **Hàm OpenCV**: `cv2.resize(img, None, fx=3, fy=3)`
- **Mục đích**:
  - Phóng to biển số lên 3 lần
  - Tăng độ phân giải để nhận dạng ký tự tốt hơn
- **Tham số**: Scale factor = 3x
- **Code**: `Test_all_images.py`, `run_image.py`

---

## 4. GIAI ĐOẠN PHÂN ĐOẠN KÝ TỰ (Character Segmentation)

### 4.1. Morphological Dilation (Lần 2)
- **Phương pháp**: Morphological Dilation
- **Hàm OpenCV**: `cv2.morphologyEx(img, cv2.MORPH_DILATE, kernel)`
- **Mục đích**:
  - Nối các phần của ký tự bị đứt đoạn
  - Tạo contour liên tục cho từng ký tự
- **Tham số**: Kernel (3x3) hình chữ nhật
- **Code**: `Test_all_images.py`, `run_image.py`

### 4.2. Tìm Contour Ký tự (Character Contour Detection)
- **Phương pháp**: Contour Finding
- **Hàm OpenCV**: `cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`
- **Mục đích**:
  - Tìm tất cả các contour trong ảnh biển số
  - Mỗi contour có thể là một ký tự
- **Tham số**:
  - Mode: `RETR_EXTERNAL` (chỉ lấy contour ngoài cùng)
- **Code**: `Test_all_images.py`, `run_image.py`

### 4.3. Bounding Rectangle (Hình chữ nhật bao quanh)
- **Phương pháp**: Bounding Box
- **Hàm OpenCV**: `cv2.boundingRect(contour)`
- **Mục đích**:
  - Tìm hình chữ nhật nhỏ nhất bao quanh ký tự
  - Lấy tọa độ (x, y, width, height)
- **Code**: `Test_all_images.py`, `run_image.py`

### 4.4. Lọc Ký tự (Character Filtering)
- **Phương pháp**: Area-based và Ratio-based Filtering
- **Tiêu chí lọc**:
  - Diện tích: `Min_char * roi_area < char_area < Max_char * roi_area`
    - Min_char = 0.01 (1% diện tích biển số)
    - Max_char = 0.09 (9% diện tích biển số)
  - Tỷ lệ: `0.25 < width/height < 0.7`
- **Mục đích**:
  - Loại bỏ nhiễu (quá nhỏ hoặc quá lớn)
  - Chỉ giữ lại ký tự có kích thước và tỷ lệ hợp lý
- **Code**: `Test_all_images.py`, `run_image.py`

### 4.5. Sắp xếp Ký tự (Character Sorting)
- **Phương pháp**: Position-based Sorting
- **Mục đích**:
  - Sắp xếp ký tự theo thứ tự từ trái sang phải (theo tọa độ x)
  - Xử lý trường hợp nhiều ký tự có cùng tọa độ x
- **Code**: `Test_all_images.py`, `run_image.py`

### 4.6. Phân loại Hàng (Line Classification)
- **Phương pháp**: Vertical Position-based Classification
- **Mục đích**:
  - Phân biệt biển số 1 hàng và 2 hàng
  - Nếu `y < height/3`: Hàng trên (first_line)
  - Nếu `y >= height/3`: Hàng dưới (second_line)
- **Code**: `Test_all_images.py`, `run_image.py`

---

## 5. GIAI ĐOẠN NHẬN DẠNG KÝ TỰ (Character Recognition)

### 5.1. Chuẩn hóa Kích thước (Size Normalization)
- **Phương pháp**: Image Resizing
- **Hàm OpenCV**: `cv2.resize(img, (20, 30))`
- **Mục đích**:
  - Chuẩn hóa kích thước tất cả ký tự về 20x30 pixels
  - Tạo vector đặc trưng đồng nhất (600 pixels)
- **Tham số**: Width = 20, Height = 30
- **Code**: `Test_all_images.py`, `run_image.py`, `GenData.py`

### 5.2. Flatten Image (Chuyển đổi thành Vector)
- **Phương pháp**: Array Reshaping
- **Hàm NumPy**: `img.reshape((1, 600))`
- **Mục đích**:
  - Chuyển ảnh 2D (20x30) thành vector 1D (600 phần tử)
  - Mỗi pixel là một đặc trưng (0 hoặc 255)
- **Code**: `Test_all_images.py`, `run_image.py`, `GenData.py`

### 5.3. K-Nearest Neighbors (KNN)
- **Phương pháp**: Machine Learning - Supervised Learning
- **Hàm OpenCV**: `cv2.ml.KNearest_create()`
- **Mục đích**:
  - Nhận dạng ký tự dựa trên khoảng cách
  - So sánh với tập dữ liệu training
- **Tham số**: 
  - K = 3 (3 láng giềng gần nhất)
  - Distance metric: Euclidean distance
- **Quy trình**:
  1. Tính khoảng cách từ ký tự cần nhận dạng đến tất cả mẫu training
  2. Sắp xếp khoảng cách tăng dần
  3. Lấy K điểm gần nhất
  4. Chọn lớp phổ biến nhất trong K điểm
- **Code**: `Test_all_images.py`, `run_image.py`, `GenData.py`

### 5.4. Chuyển đổi ASCII (ASCII Conversion)
- **Phương pháp**: Character Encoding
- **Hàm Python**: `chr(int(ascii_code))`
- **Mục đích**:
  - Chuyển đổi mã ASCII thành ký tự
  - Kết quả cuối cùng là text của biển số
- **Code**: `Test_all_images.py`, `run_image.py`

---

## 6. CÁC PHƯƠNG PHÁP HỖ TRỢ KHÁC

### 6.1. Image Resizing (Resize ảnh gốc)
- **Phương pháp**: Scale Transformation
- **Hàm OpenCV**: `cv2.resize(img, (1920, 1080))`
- **Mục đích**:
  - Chuẩn hóa kích thước ảnh đầu vào
  - Đảm bảo xử lý nhất quán
- **Tham số**: Width = 1920, Height = 1080
- **Code**: Tất cả các file chính

### 6.2. Image Copying
- **Phương pháp**: Deep Copy
- **Hàm NumPy**: `img.copy()`
- **Mục đích**:
  - Tạo bản sao ảnh gốc để xử lý
  - Giữ nguyên ảnh gốc cho các bước sau
- **Code**: `Test_all_images.py`, `run_image.py`

### 6.3. Structuring Element
- **Phương pháp**: Kernel Creation
- **Hàm OpenCV**: `cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))`
- **Mục đích**:
  - Tạo kernel cho các phép toán hình thái học
  - Hình dạng: Hình chữ nhật (MORPH_RECT)
- **Tham số**: Size (3x3)
- **Code**: `Preprocess.py`, `Test_all_images.py`

---

## Tổng kết

### Các phương pháp chính:
1. ✅ **Color Space Conversion** (BGR → HSV)
2. ✅ **Morphological Operations** (Top Hat, Black Hat, Dilation)
3. ✅ **Gaussian Blur** (Noise Reduction)
4. ✅ **Adaptive Threshold** (Binarization)
5. ✅ **Canny Edge Detection** (Edge Detection)
6. ✅ **Contour Detection & Analysis** (Shape Detection)
7. ✅ **Polygon Approximation** (Shape Simplification)
8. ✅ **Affine Transformation** (Rotation, Resize)
9. ✅ **Image Masking & Cropping** (Region Extraction)
10. ✅ **Character Segmentation** (Contour-based)
11. ✅ **Size Normalization** (Standardization)
12. ✅ **K-Nearest Neighbors** (Machine Learning)

### Thư viện sử dụng:
- **OpenCV (cv2)**: Xử lý ảnh chính
- **NumPy**: Tính toán số học và mảng
- **KNN (OpenCV ML)**: Nhận dạng ký tự

### Pipeline xử lý:
```
Ảnh gốc → HSV Conversion → Contrast Enhancement → 
Gaussian Blur → Adaptive Threshold → Canny Edge → 
Dilation → Contour Detection → Polygon Approximation → 
Plate Extraction → Rotation → Resize → 
Character Segmentation → Normalization → KNN Recognition → 
Text Output
```

---

## Tài liệu tham khảo

- OpenCV Documentation: https://docs.opencv.org/
- Morphological Operations: https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
- Canny Edge Detection: https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html
- K-Nearest Neighbors: https://docs.opencv.org/4.x/d5/d26/tutorial_py_knn_understanding.html

