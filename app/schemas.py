from pydantic import BaseModel

class MarkdownRequest(BaseModel):
    md_content: str

class HTMLResponse(BaseModel):
    html_content: str
    message: str = "Success"

class HTMLRequest(BaseModel):
    html_content: str