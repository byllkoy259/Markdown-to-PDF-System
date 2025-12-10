from fastapi import APIRouter, HTTPException, status, Response, UploadFile, File
from app.schemas import MarkdownRequest, HTMLResponse, HTMLRequest
from app.services.converter import converter_service
from app.services.pdf_generator import pdf_service
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/export/md-html", response_model=HTMLResponse)
async def convert_markdown(request: MarkdownRequest):
    """
    API nhận vào Markdown và trả về HTML.
    """
    try:
        html_result = converter_service.convert_to_html(request.md_content)
        
        return HTMLResponse(
            html_content=html_result,
            message="Chuyển đổi thành công"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý markdown: {str(e)}"
        )
    
    
@router.post("/export/html-pdf")
async def export_html_to_pdf(request: HTMLRequest, show_page_number: bool = True):
    """
    API nhận vào chuỗi HTML thô và xuất ra PDF trực tiếp.
    Bỏ qua bước convert Markdown.
    """
    try:
        pdf_bytes = pdf_service.generate_pdf(request.html_content, show_page_number=show_page_number)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=export_from_html.pdf"
            }
        )
    except Exception as e:
        print(f"Error generating PDF from HTML: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo PDF từ HTML: {str(e)}"
        )
    

@router.post("/export/md-pdf")
async def export_pdf(request: MarkdownRequest):
    """
    API nhận vào Markdown, convert sang HTML, sau đó xuất ra file PDF.
    """
    try:
        html_content = converter_service.convert_to_html(request.md_content)
        
        pdf_bytes = pdf_service.generate_pdf(html_content)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=export_document.pdf"
            }
        )
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo PDF: {str(e)}"
        )


@router.post("/upload/md-html")
async def upload_markdown_convert(file: UploadFile = File(...)):
    """
    Upload file .md và nhận về file .html để tải xuống.
    """
    if not file.filename.endswith((".md", ".markdown", ".txt")):
        raise HTTPException(status_code=400, detail="File phải có định dạng .md, .markdown hoặc .txt")

    try:
        content_bytes = await file.read()
        content_str = content_bytes.decode("utf-8")
        
        html_result = converter_service.convert_to_html(content_str)
        
        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"{base_name}.html"

        return Response(
            content=html_result,
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File không phải định dạng UTF-8 hợp lệ.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý file: {str(e)}")


@router.post("/upload/html-pdf")
async def upload_html_to_pdf(file: UploadFile = File(...), show_page_number: bool = True):
    """
    Upload file .html và nhận về file PDF.
    """
    if not file.filename.endswith((".html", ".htm")):
        raise HTTPException(status_code=400, detail="File phải có định dạng .html hoặc .htm")

    try:
        content_bytes = await file.read()
        content_str = content_bytes.decode("utf-8")
        
        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"{base_name}.pdf"

        pdf_bytes = pdf_service.generate_pdf(content_str, show_page_number=show_page_number)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File HTML phải có encoding UTF-8.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo PDF: {str(e)}")


@router.post("/upload/md-pdf")
async def upload_md_to_pdf(file: UploadFile = File(...), show_page_number: bool = True):
    """
    Upload file .md, .markdown hoặc .txt và nhận về file PDF.
    """
    if not file.filename.endswith((".md", ".markdown", ".txt")):
        raise HTTPException(status_code=400, detail="File phải có định dạng .md, .markdown hoặc .txt")

    try:
        content_bytes = await file.read()
        content_str = content_bytes.decode("utf-8")
        
        html_content = converter_service.convert_to_html(content_str)
        
        pdf_bytes = pdf_service.generate_pdf(html_content, show_page_number=show_page_number)
        
        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"{base_name}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File không phải định dạng UTF-8 hợp lệ.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo PDF từ file Markdown: {str(e)}")


@router.post("/upload/merge-pdf")
async def upload_and_merge_pdfs(
    body_file: UploadFile = File(..., description="File PDF nội dung chính."),
    footer_file: UploadFile = File(..., description="File PDF chứa footer (1 trang).")
):
    """
    Upload 2 file PDF để hợp nhất. Trang cuối của file nội dung sẽ được
    phủ lên trên trang đầu của file footer.
    """
    if not body_file.filename.endswith(".pdf") or not footer_file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Cả hai file tải lên phải có định dạng .pdf")

    try:
        body_bytes = await body_file.read()
        footer_bytes = await footer_file.read()

        merged_pdf_bytes = pdf_service.merge_with_footer(body_bytes, footer_bytes)

        base_name = os.path.splitext(body_file.filename)[0]
        output_filename = f"{base_name}_merged.pdf"

        return Response(
            content=merged_pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
    except Exception as e:
        logger.error(f"Lỗi khi hợp nhất PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi hợp nhất PDF: {str(e)}")