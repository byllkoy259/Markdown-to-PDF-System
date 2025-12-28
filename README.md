# Hệ thống chuyển đổi Markdown sang PDF

## 1. Giới thiệu

Đây là một API Backend Service chuyên nghiệp phục vụ việc chuyển đổi tài liệu và quản lý file. Hệ thống được thiết kế theo kiến trúc Microservices, đóng gói hoàn toàn bằng Docker.

**Chức năng chính:**
- **Chuyển đổi:** Markdown $\rightarrow$ HTML $\rightarrow$ PDF (sử dụng `WeasyPrint` & `Mistune`).
- **Quản lý:** Lưu trữ file tại MinIO (S3 Compatible) và metadata tại PostgreSQL.
- **Tiện ích:** Versioning tài liệu, Merge PDF, đánh số trang.

## 2. Công nghệ sử dụng

- **Ngôn ngữ:** Python 3.10+
- **Package Manager:** `uv`
- **Framework:** FastAPI
- **Database:** PostgreSQL (Driver: `psycopg2-binary`, ORM: `SQLAlchemy`)
- **Object Storage:** MinIO (S3 Compatible)
- **PDF Processing:** 
  - `WeasyPrint` (Tạo PDF từ HTML)
  - `pypdf` (Xử lý, cắt ghép file PDF)
- **Markdown Processing:** `mistune` (Parse Markdown sang HTML)
- **Infrastructure:** Docker & Docker Compose
- **Gateway (Tùy chọn):** Nginx hoặc Traefik.

## 3. Quản lý Nhánh

Dự án được chia thành 3 nhánh để demo các giải pháp hạ tầng khác nhau:

| Nhánh | Mô tả | Gateway | URL Truy cập chính |
| :--- | :--- | :--- | :--- |
| **`main`** | Cơ bản, không dùng Proxy. Phù hợp Dev/Debug. | Không | `localhost:8000` |
| **`opt/nginx`** | Sử dụng Nginx làm Gateway (Reverse Proxy). Cấu hình tĩnh. | **Nginx** | `127.0.0.1.nip.io` |
| **`opt/traefik`** | Sử dụng Traefik làm Gateway. Cấu hình động (Cloud-native). | **Traefik** | `127.0.0.1.nip.io` |

---

## 4. Hướng dẫn cài đặt và chạy code

### Bước 1: Chuẩn bị môi trường

1. **Cài đặt Docker Desktop:** Đảm bảo Docker đã chạy.
2. **Cài đặt `uv` (Windows PowerShell):**
    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

### Bước 2: Clone repository
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```

### Bước 2: Cấu hình biến môi trường
    ```bash
    cp .env.example .env
    ```

## 5. Hướng dẫn chạy từng nhánh

### Nhánh 1: main

1. **Chuyển nhánh:**
    ```bash
    git checkout main
    ```

2. **Đồng bộ thư viện (Optional):**
    ```bash
    uv sync
    ```

3. **Khởi chạy Docker:**
    ```bash
    docker compose up -d --build
    ```

4. **Truy cập:**
- **Backend API:** http://127.0.0.1:8000/docs
- **MinIO Console:** http://127.0.0.1:9001

### Nhánh 2: opt/nginx

1. **Chuyển nhánh:**
    ```bash
    git checkout opt/nginx
    ```

2. **Khởi chạy Docker:**
    ```bash
    docker compose up -d --build
    ```

3. **Truy cập:**
- **Backend API:** http://127.0.0.1.nip.io/docs
- **MinIO Console:** http://minio.127.0.0.1.nip.io

### Nhánh 3: opt/traefik

1. **Chuyển nhánh:**
    ```bash
    git checkout opt/traefik
    ```

2. **Khởi chạy Docker:**
    ```bash
    docker compose up -d --build
    ```

3. **Truy cập:**
- **Backend API:** http://127.0.0.1.nip.io/docs
- **MinIO Console:** http://minio.127.0.0.1.nip.io
- **Traefik Dashboard:** http://localhost:8080 (Để xem sơ đồ hệ thống).

## 6. Người hướng dẫn

**Mentor:** Phạm Tiến Thành (VNPT-IT)
