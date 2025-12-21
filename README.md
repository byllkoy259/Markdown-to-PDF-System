# Hệ thống chuyển đổi Markdown sang PDF

## 1. Mục đích

Xây dựng một API service backend chuyên nghiệp để thực hiện các chức năng:
- **Chuyển đổi:** Markdown $\rightarrow$ HTML $\rightarrow$ PDF.
- **Quản lý:** Lưu trữ tài liệu có cấu trúc vào Cơ sở dữ liệu (PostgreSQL) và File server (MinIO).
- **Versioning:** Tự động quản lý phiên bản (v1, v2...) khi cập nhật nội dung.
- **Tiện ích:** Hỗ trợ upload file, merge (ghép) PDF footer/header, và đánh số trang.

## 2. Công nghệ sử dụng

- **Ngôn ngữ:** Python 3.10+
- **Framework:** FastAPI
- **Database:** PostgreSQL (Driver: `psycopg2-binary`, ORM: `SQLAlchemy`)
- **Object Storage:** MinIO (S3 Compatible)
- **PDF Processing:** 
  - `WeasyPrint` (Tạo PDF từ HTML)
  - `pypdf` (Xử lý, cắt ghép file PDF)
- **Markdown Processing:** `mistune` (Parse Markdown sang HTML)
- **Infrastructure:** Docker & Docker Compose

## 3. Cấu trúc dự án

```
.
├── app/
│   ├── api/
│   │   ├── documents.py     # API quản lý tài liệu
│   │   └── routes.py        # API tiện ích nhanh (Convert không lưu DB)
│   ├── core/
│   │   ├── config.py        # Cấu hình hệ thống (Load từ .env)
│   │   └── database.py      # Thiết lập kết nối Database
│   ├── services/
│   │   ├── converter.py     # Logic chuyển đổi Markdown -> HTML (Mistune)
│   │   ├── pdf_generator.py # Logic tạo PDF (WeasyPrint) và Merge PDF
│   │   └── storage.py       # Logic giao tiếp với MinIO
│   ├── main.py              # Khởi tạo ứng dụng FastAPI
│   ├── models.py            # Định nghĩa Database Models
│   ├── schemas.py           # Định nghĩa Pydantic Schemas
│   └── utils.py             # Các hàm tiện ích
├── .env                     # Biến môi trường (Chứa mật khẩu - Không commit)
├── .env.example             # File mẫu cấu hình (Có commit)
├── .gitignore               # Cấu hình git ignore
├── docker-compose.yml       # Cấu hình Docker (DB & MinIO)
└── requirements.txt         # Danh sách thư viện
```

## 4. Hướng dẫn cài đặt và chạy code

### Bước 1: Chuẩn bị môi trường

1.  **Clone repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```

2.  **Tạo và kích hoạt môi trường ảo:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Trên Windows: .\venv\Scripts\activate
    ```

3.  **Cài đặt các thư viện:**
    ```bash
    pip install -r requirements.txt
    ```

### Bước 2: Khởi chạy hạ tầng

1. **Khởi động container:**
    ```bash
    docker-compose up -d
    ```

2. **Kiểm tra:**
- **PostgreSQL** chạy tại cổng: 5433 (hoặc theo config trong docker-compose).
- **MinIO** chạy tại cổng: 9000.
- **MinIO Console** chạy tại cổng: 9001 (Truy cập web: http://127.0.0.1:9001).

### Bước 3: Cấu hình biến môi trường

1.  **Tạo file `.env`:**
    ```bash
    cp .env.example .env
    ```

2.  **Chạy server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    API sẽ có tại `http://127.0.0.1:8000` và tài liệu Swagger UI tại `http://127.0.0.1:8000/docs#`.

## 5. Người hướng dẫn

**Mentor:** Phạm Tiến Thành (VNPT-IT)
