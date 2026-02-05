"""
PDF 轉文字 API 服務

提供 RESTful API 用於將 PDF 檔案轉換為純文字。
支援密碼保護的 PDF 檔案。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import pdf


# 建立 FastAPI 應用程式
app = FastAPI(
    title="PDF 轉文字 API",
    description="將 PDF 檔案轉換為純文字的 API 服務，支援密碼保護的 PDF。",
    version="1.0.0"
)

# 配置 CORS 中間件，允許跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應限制特定來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載 PDF 路由
app.include_router(pdf.router)


@app.get("/", tags=["健康檢查"])
async def root():
    """
    根端點 - 健康檢查

    Returns:
        API 服務狀態訊息
    """
    return {
        "service": "PDF 轉文字 API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["健康檢查"])
async def health_check():
    """
    健康檢查端點

    Returns:
        健康狀態
    """
    return {"status": "healthy"}
