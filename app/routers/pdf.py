"""
PDF API 路由模組

提供 PDF 相關的 RESTful API 端點。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from ..services.pdf_extractor import extract_text_from_base64_pdf, PDFExtractionError


# 建立路由器
router = APIRouter(
    prefix="/pdf",
    tags=["PDF"]
)


class PDFToTextRequest(BaseModel):
    """PDF 轉文字請求模型"""
    pdf: str = Field(
        ...,
        description="Base64 編碼的 PDF 檔案內容"
    )
    passwords: Optional[list[str]] = Field(
        default=[],
        description="PDF 密碼列表，用於解密受保護的 PDF"
    )


class PDFToTextResponse(BaseModel):
    """PDF 轉文字回應模型"""
    text: str = Field(
        ...,
        description="從 PDF 提取的文字內容"
    )


@router.post(
    "/toText",
    response_model=PDFToTextResponse,
    summary="PDF 轉文字",
    description="接收 Base64 編碼的 PDF 檔案，回傳提取的文字內容"
)
async def pdf_to_text(request: PDFToTextRequest) -> PDFToTextResponse:
    """
    將 PDF 轉換為純文字

    接收 Base64 編碼的 PDF 檔案和可選的密碼列表，
    回傳提取的文字內容。

    Args:
        request: 包含 PDF 資料和密碼的請求物件

    Returns:
        包含提取文字的回應物件

    Raises:
        HTTPException: 處理失敗時回傳 400 錯誤
    """
    try:
        # 提取文字
        text = extract_text_from_base64_pdf(
            pdf_base64=request.pdf,
            passwords=request.passwords
        )

        return PDFToTextResponse(text=text)

    except PDFExtractionError as e:
        # PDF 處理相關錯誤
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # 其他未預期的錯誤
        raise HTTPException(
            status_code=500,
            detail=f"處理 PDF 時發生錯誤: {str(e)}"
        )
