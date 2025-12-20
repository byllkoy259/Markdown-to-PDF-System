import os

class Settings:
    # Database Config
    DATABASE_URL = "postgresql://baoden:123456789@127.0.0.1:5433/markdown_db"
    
    # MinIO Config
    MINIO_ENDPOINT = "127.0.0.1:9000"
    MINIO_ACCESS_KEY = "minioadmin"
    MINIO_SECRET_KEY = "123456789"
    MINIO_BUCKET_NAME = "pdf-reports"
    MINIO_SECURE = False  # Đặt True nếu dùng HTTPS

settings = Settings()