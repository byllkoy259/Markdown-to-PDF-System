from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class MarkdownRequest(BaseModel):
    md_content: str

class HTMLResponse(BaseModel):
    html_content: str
    message: str = "Success"

class HTMLRequest(BaseModel):
    html_content: str

class DocumentCreate(BaseModel):
    title: str
    content: str
    content_format: str = "markdown"
    show_page_number: bool = True

class DocumentUpdate(BaseModel):
    md_content: str
    content_format: str = "markdown"
    show_page_number: bool = True

class DocumentVersionResponse(BaseModel):
    version_number: int
    created_at: datetime
    download_url: Optional[str] = None

class DocumentResponse(BaseModel):
    id: int
    title: str
    current_content: str
    content_format: str
    current_version: int
    show_page_number: bool
    updated_at: datetime
    # versions: List[DocumentVersionResponse] = [] # Optional nếu muốn load hết