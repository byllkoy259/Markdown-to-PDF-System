FROM python:3.10-slim-bookworm

# Cài đặt uv vào trong Docker
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Thiết lập biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Đặt môi trường ảo của uv làm mặc định
ENV VIRTUAL_ENV=/code/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Cài đặt các thư viện hệ thống cần thiết cho WeasyPrint và PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc trong Container
WORKDIR /code

# Copy file quản lý package của uv
COPY pyproject.toml uv.lock /code/

# Cài đặt thư viện Python bằng uv
RUN uv sync --frozen --no-install-project

# Copy toàn bộ mã nguồn vào Container
COPY ./app /code/app

# Chạy lệnh cuối để uv nhận diện project (nếu cần) và hoàn tất
RUN uv sync --frozen

# Mở cổng 8000
EXPOSE 8000

# Lệnh chạy ứng dụng khi container khởi động
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]