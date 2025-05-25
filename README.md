foody app
![image](https://github.com/user-attachments/assets/dd2b1e73-e060-4395-b779-40069e619a0b)


# Hệ thống Đặt Món Ăn và Đánh Giá Nhà Hàng + Quản lý vật phẩm theo dõi đơn hàng cho chủ cửa hàng

## Giới thiệu

Hệ thống đặt món ăn và đánh giá nhà hàng là một dự án hoàn chỉnh cho phép người dùng tìm kiếm, duyệt và đặt món trực tuyến tại các nhà hàng. Người dùng có thể xem danh sách nhà hàng, xem thực đơn chi tiết và đặt món (với tùy chọn mang đi hoặc giao hàng). Đồng thời, sau khi trải nghiệm, người dùng có thể đánh giá và bình luận về chất lượng dịch vụ và món ăn. Đối với nhà hàng, hệ thống cung cấp chức năng nhận và quản lý đơn hàng, giúp cải thiện quy trình vận hành. Dự án sử dụng **FastAPI** cho phần backend và **Kivy** cho giao diện người dùng, hướng đến một ứng dụng đa nền tảng, dễ triển khai và mở rộng.

## Các tính năng chính

* **Đăng ký và đăng nhập:** Hỗ trợ phân quyền người dùng và nhà hàng, bảo mật dữ liệu cá nhân.
* **Xem danh sách nhà hàng:** Hiển thị thông tin cơ bản của các nhà hàng (tên, địa chỉ, đánh giá trung bình).
* **Xem chi tiết nhà hàng:** Bao gồm thông tin chi tiết và thực đơn món ăn của nhà hàng.
* **Đặt món ăn trực tuyến:** Cho phép người dùng thêm món vào giỏ hàng và thanh toán đơn hàng.
* **Quản lý đơn hàng:** Người dùng có thể theo dõi trạng thái đơn hàng; nhà hàng có thể nhận và cập nhật trạng thái đơn (mới, đang xử lý, hoàn thành, v.v.).
* **Đánh giá và bình luận:** Sau khi nhận món, người dùng có thể gửi đánh giá (sao) và nhận xét về trải nghiệm ăn uống.
* **...

## Công nghệ sử dụng

* **Python**: Ngôn ngữ chính để phát triển cả backend và frontend.
* **FastAPI** – khung web Python hiện đại, hiệu năng cao (xây dựng API RESTful).
* **Kivy** – framework mã nguồn mở để phát triển ứng dụng GUI đa nền tảng (Windows, Linux, Android, iOS) bằng Python.
* **SQLite** – Cơ sở dữ liệu SQL nhúng, nhẹ và đáng tin cậy, lưu trữ đơn giản trong một tập tin.
* **Các thư viện bổ trợ**:Pydantic (validate dữ liệu), Uvicorn (ASGI server cho FastAPI), v.v.

## Hướng dẫn cài đặt và chạy dự án

1. **Yêu cầu**: Cài đặt Python 3.8 hoặc cao hơn.
2. **Cài đặt mã nguồn**: Tải hoặc clone repository về máy và chuyển vào thư mục dự án.
3. **Cài đặt thư viện**: Chạy `pip install -r requirements.txt` để cài đặt c.
4. **Khởi chạy backend**
5. **Khởi chạy giao diện Kivy**: Vào thư mục frontend (hoặc nơi chứa file giao diện), chạy lệnh `python main.py`. Ứng dụng sẽ kết nối tới backend và hiển thị giao diện người dùng.

## Hướng dẫn API

Các endpoint chính bao gồm:

* `GET /restaurants` – Lấy danh sách tất cả các nhà hàng.
* `GET /restaurants/{id}` – Lấy thông tin chi tiết của một nhà hàng (bao gồm thực đơn).
* `POST /orders` – Tạo mới một đơn hàng. Định dạng yêu cầu gồm thông tin người dùng, nhà hàng và danh sách món.
* `GET /orders/{id}` – Lấy thông tin chi tiết của đơn hàng theo mã đơn.
* `GET /orders` – Lấy danh sách các đơn hàng của người dùng (hoặc tất cả đơn hàng nếu là admin).
* `GET /restaurants/{id}/reviews` – Lấy danh sách đánh giá đã gửi cho nhà hàng.
* `POST /restaurants/{id}/reviews` – Người dùng gửi đánh giá (số sao, nhận xét) cho nhà hàng.

Mỗi endpoint đều yêu cầu phương thức HTTP tương ứng và có thể thử nghiệm trực tiếp. Ngoài ra, FastAPI hỗ trợ đầy đủ các phương thức PUT/PATCH/DELETE nếu cần cho các chức năng mở rộng như sửa đơn hàng, xóa đánh giá, v.v.

## Cấu trúc thư mục

Hệ thống/  
├── backend/             # Mã nguồn FastAPI cho phần server  
│   ├── main.py          # Ứng dụng FastAPI chính        
│   └── ...             
├── frontend/            # Mã nguồn Kivy cho giao diện người dùng  
│   ├── main.py          # Ứng dụng Kivy chính  
│   └── ...             # Các module hỗ trợ giao diện (widgets, screens, services)  
└── README.md            # Tài liệu hướng dẫn (file này)  

## Hình ảnh minh họa từ APP
![image](https://github.com/user-attachments/assets/733c661a-e447-421b-951b-1e42c1616020)
![image](https://github.com/user-attachments/assets/4ec6d740-d619-45f5-b485-f5e4d765fa62)
![image](https://github.com/user-attachments/assets/838dce49-e380-41ae-83ec-f928035a2157)
![image](https://github.com/user-attachments/assets/eefdf5f2-a78f-4a36-983e-75ef442cf759)

