from fastapi import FastAPI
from app.api.routes import router as conversion_router

app = FastAPI(
    title="Markdown to PDF System",
    description="Hệ thống chuyển đổi Markdown sang PDF",
    version="1.0.0"
)

# Prefix "/api/v1" giúp quản lý phiên bản API dễ dàng hơn
app.include_router(conversion_router, prefix="/api/v1", tags=["Conversion"])

@app.get("/")
async def root():
    return {"message": "Hệ thống đang hoạt động. Truy cập /docs để xem API."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)