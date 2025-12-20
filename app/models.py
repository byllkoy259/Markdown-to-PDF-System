from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    current_content = Column(Text) # Nội dung có thể là markdown hoặc HTML
    content_format = Column(String, default="markdown") # 'markdown' hoặc 'html'
    current_version = Column(Integer, default=0)
    show_page_number = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions = relationship("DocumentVersion", back_populates="document")

class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    version_number = Column(Integer)
    minio_path = Column(String) # Đường dẫn file PDF
    source_path = Column(String) # Đường dẫn file gốc
    source_extension = Column(String) # Loại file gốc
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="versions")