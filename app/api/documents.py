from fastapi import APIRouter, Depends, Form, HTTPException, Response, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models import Document, DocumentVersion
from app.schemas import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentVersionResponse
from app.services.converter import converter_service
from app.services.pdf_generator import pdf_service
from app.services.storage import storage_service
from app.utils import slugify
import os
import json

router = APIRouter()

# Hàm dùng chung để tạo Document
def process_create_document(
    db: Session, 
    title: str, 
    content: str, 
    fmt: str, 
    show_page_number: bool,
    source_original_bytes: bytes = None, 
    source_extension: str = ".txt"
):
    # Tạo Slug cho Title
    safe_title = slugify(title)

    # Lưu vào DB
    new_doc = Document(
        title=title,
        current_content=content,
        content_format=fmt,
        show_page_number=show_page_number,
        current_version=1
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    folder_name = f"{safe_title}_{new_doc.id}"

    try:
        if source_original_bytes is None:
            source_data = content.encode('utf-8')
        else:
            source_data = source_original_bytes

        # Định nghĩa đường dẫn Source
        source_object_name = f"sources/{folder_name}/v1_source{source_extension}"
        storage_service.upload_pdf(source_data, source_object_name)
        
        # Tạo và lưu PDF
        if fmt == "markdown":
            html_content_for_pdf = converter_service.convert_to_html(new_doc.current_content)
        else:
            html_content_for_pdf = new_doc.current_content

        pdf_bytes = pdf_service.generate_pdf(html_content_for_pdf, show_page_number=show_page_number)

        # Upload lên MinIO
        pdf_object_name = f"documents/{folder_name}/v1.pdf"
        storage_service.upload_pdf(pdf_bytes, pdf_object_name)

        # Lưu lịch sử Version
        version_entry = DocumentVersion(
            document_id=new_doc.id,
            version_number=1,
            minio_path=pdf_object_name,
            source_path=source_object_name,
            source_extension=fmt
        )
        db.add(version_entry)
        db.commit()
        
        return new_doc
        
    except Exception as e:
        db.delete(new_doc)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý tài liệu: {str(e)}")


@router.post("/", response_model=DocumentResponse)
def create_document(doc_in: DocumentCreate, db: Session = Depends(get_db)):
    """
    Tạo Document từ nội dung thô (Markdown hoặc HTML)
    """
    ext = ".md" if doc_in.content_format == "markdown" else ".html"
    
    # Nếu người dùng nhập JSON string, ta có thể lưu file gốc là .json
    try:
        json.loads(doc_in.content)
        ext = ".json"
    except ValueError:
        pass

    return process_create_document(
        db=db, 
        title=doc_in.title, 
        content=doc_in.content, 
        fmt=doc_in.content_format,
        show_page_number=doc_in.show_page_number,
        source_original_bytes=None,
        source_extension=ext
    )


@router.post("/upload", response_model=DocumentResponse)
async def create_document_from_file(
    file: UploadFile = File(...), 
    show_page_number: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Tạo Document từ file upload (.md, .html, .txt)
    """
    filename = file.filename.lower()
    base_name, ext = os.path.splitext(file.filename)
    
    if filename.endswith((".md", ".markdown", ".txt")):
        fmt = "markdown"
    elif filename.endswith((".html", ".htm")):
        fmt = "html"
    elif filename.endswith(".json"):
        fmt = "markdown"
    else:
        raise HTTPException(status_code=400, detail="Định dạng không hỗ trợ.")

    content_bytes = await file.read()
    content_str = content_bytes.decode("utf-8")

    return process_create_document(
        db=db, 
        title=base_name, 
        content=content_str, 
        fmt=fmt,
        show_page_number=show_page_number,
        source_original_bytes=content_bytes,
        source_extension=ext
    )


@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document(doc_id: int, doc_in: DocumentUpdate, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")

    new_version = doc.current_version + 1
    safe_title = slugify(doc.title)
    folder_name = f"{safe_title}_{doc.id}"

    source_ext = ".md" if doc_in.content_format == "markdown" else ".html"
    source_object_name = f"sources/{folder_name}/v{new_version}_source{source_ext}"
    source_data = doc_in.content.encode('utf-8')
    storage_service.upload_pdf(source_data, source_object_name)

    if doc_in.content_format == "markdown":
        html_content = converter_service.convert_to_html(doc_in.content)
    else:
        html_content = doc_in.content

    pdf_bytes = pdf_service.generate_pdf(html_content, show_page_number=doc_in.show_page_number)

    pdf_object_name = f"documents/{folder_name}/v{new_version}.pdf"
    storage_service.upload_pdf(pdf_bytes, pdf_object_name)

    version_entry = DocumentVersion(
        document_id=doc.id,
        version_number=new_version,
        minio_path=pdf_object_name,
        source_path=source_object_name,
        source_extension=doc_in.content_format
    )
    db.add(version_entry)

    doc.current_content = doc_in.content
    doc.content_format = doc_in.content_format
    doc.show_page_number = doc_in.show_page_number
    doc.current_version = new_version
    
    db.commit()
    db.refresh(doc)
    return doc


@router.put("/{doc_id}/upload", response_model=DocumentResponse)
async def update_document_from_file(
    doc_id: int,
    file: UploadFile = File(...),
    show_page_number: bool = Form(True),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")

    filename = file.filename.lower()
    base_name, ext = os.path.splitext(file.filename)
    
    if filename.endswith((".md", ".markdown", ".txt")):
        fmt = "markdown"
        source_ext = ".md"
    elif filename.endswith((".html", ".htm")):
        fmt = "html"
        source_ext = ".html"
    else:
        raise HTTPException(status_code=400, detail="Định dạng không hỗ trợ")

    content_bytes = await file.read()
    content_str = content_bytes.decode("utf-8")

    new_version = doc.current_version + 1
    safe_title = slugify(doc.title)
    folder_name = f"{safe_title}_{doc.id}"

    source_object_name = f"sources/{folder_name}/v{new_version}_source{source_ext}"
    storage_service.upload_pdf(content_bytes, source_object_name)

    if fmt == "markdown":
        html_content = converter_service.convert_to_html(content_str)
    else:
        html_content = content_str
        
    pdf_bytes = pdf_service.generate_pdf(html_content, show_page_number=show_page_number)

    pdf_object_name = f"documents/{folder_name}/v{new_version}.pdf"
    storage_service.upload_pdf(pdf_bytes, pdf_object_name)

    version_entry = DocumentVersion(
        document_id=doc.id,
        version_number=new_version,
        minio_path=pdf_object_name,
        source_path=source_object_name,
        source_extension=fmt
    )
    db.add(version_entry)

    doc.current_content = content_str
    doc.content_format = fmt
    doc.show_page_number = show_page_number
    doc.current_version = new_version

    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document_detail(doc_id: int, db: Session = Depends(get_db)):
    """
    API này trả về toàn bộ thông tin hiện tại của Document.
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")
    return doc


@router.get("/{doc_id}/source")
def get_document_source(doc_id: int, version: int = None, db: Session = Depends(get_db)):
    query = db.query(DocumentVersion).filter(DocumentVersion.document_id == doc_id)
    if version:
        version_record = query.filter(DocumentVersion.version_number == version).first()
    else:
        version_record = query.order_by(DocumentVersion.version_number.desc()).first()

    if not version_record or not version_record.source_path:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên bản tài liệu.")

    file_content = storage_service.get_file_content(version_record.source_path)
    
    if not file_content:
        raise HTTPException(status_code=500, detail="Lỗi kết nối MinIO")

    base_name = os.path.basename(version_record.source_path)

    return Response(
        content=file_content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={base_name}"
        }
    )


@router.get("/{doc_id}/pdf")
def get_document_pdf(doc_id: int, version: int = None, db: Session = Depends(get_db)):
    query = db.query(DocumentVersion).filter(DocumentVersion.document_id == doc_id)
    if version:
        version_record = query.filter(DocumentVersion.version_number == version).first()
    else:
        version_record = query.order_by(DocumentVersion.version_number.desc()).first()

    if not version_record:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên bản tài liệu.")

    file_content = storage_service.get_file_content(version_record.minio_path)
    
    if not file_content:
         raise HTTPException(status_code=500, detail="Lỗi kết nối MinIO")

    return Response(
        content=file_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=document_v{version_record.version_number}.pdf"
        }
    )


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """
    Xóa tài liệu hoàn toàn:
    1. Xóa các file liên quan trên MinIO.
    2. Xóa dữ liệu trong Database.
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")

    # Lấy danh sách các version để xóa file trên MinIO
    versions = db.query(DocumentVersion).filter(DocumentVersion.document_id == doc_id).all()
    
    for v in versions:
        if v.minio_path:
            storage_service.client.remove_object(settings.MINIO_BUCKET_NAME, v.minio_path)
        if v.source_path:
            storage_service.client.remove_object(settings.MINIO_BUCKET_NAME, v.source_path)

    # Xóa dữ liệu trong Database
    db.query(DocumentVersion).filter(DocumentVersion.document_id == doc_id).delete()
    db.delete(doc)
    
    db.commit()
    return None