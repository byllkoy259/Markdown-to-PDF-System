from fastapi import FastAPI
from app.core.database import Base, engine
from app.api.documents import router as document_router
from app.api.routes import router as conversion_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Markdown to PDF System",
    description="Hệ thống chuyển đổi Markdown sang PDF",
    version="2.0.0"
)

app.include_router(conversion_router, prefix="/api/v1/tools", tags=["Tools"])

app.include_router(document_router, prefix="/api/v1/documents", tags=["Documents"])

@app.get("/")
async def root():
    return {"message": "Hệ thống đang hoạt động. Truy cập /docs để xem API."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)