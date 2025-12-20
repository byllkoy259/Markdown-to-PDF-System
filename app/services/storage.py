from minio import Minio
from app.core.config import settings
import io
from datetime import timedelta

class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
            self.client.make_bucket(settings.MINIO_BUCKET_NAME)

    def upload_pdf(self, file_data: bytes, object_name: str):
        """Upload file bytes lên MinIO"""
        file_stream = io.BytesIO(file_data)
        self.client.put_object(
            settings.MINIO_BUCKET_NAME,
            object_name,
            file_stream,
            length=len(file_data),
            content_type="application/pdf"
        )
        return object_name

    def get_presigned_url(self, object_name: str):
        """Lấy link tạm thời để xem file"""
        return self.client.get_presigned_url(
            "GET",
            settings.MINIO_BUCKET_NAME,
            object_name,
            expires=timedelta(hours=1)
        )
    
    def get_file_content(self, object_name: str):
        try:
            response = self.client.get_object(settings.MINIO_BUCKET_NAME, object_name)
            return response.read()
        except Exception as e:
            print(f"MinIO Error: {e}")
            return None
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()

storage_service = StorageService()