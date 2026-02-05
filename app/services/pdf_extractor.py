"""
PDF 文字提取服務模組

提供 PDF 解密和文字提取功能，支援多種加密方式（RC4/AES）。
"""

import base64
from typing import Optional

import fitz  # PyMuPDF


class PDFExtractionError(Exception):
    """PDF 提取錯誤的自訂例外類別"""
    pass


def decode_base64_pdf(pdf_base64: str) -> bytes:
    """
    將 Base64 編碼的 PDF 字串解碼為位元組

    Args:
        pdf_base64: Base64 編碼的 PDF 字串

    Returns:
        解碼後的 PDF 位元組

    Raises:
        PDFExtractionError: Base64 解碼失敗時拋出
    """
    try:
        return base64.b64decode(pdf_base64)
    except Exception as e:
        raise PDFExtractionError(f"Base64 解碼失敗: {str(e)}")


def extract_text_from_pdf(pdf_bytes: bytes, passwords: Optional[list[str]] = None) -> str:
    """
    從 PDF 位元組中提取文字

    支援密碼保護的 PDF 檔案。會依序嘗試提供的密碼列表，
    直到成功解密或所有密碼都嘗試失敗。

    Args:
        pdf_bytes: PDF 檔案的位元組內容
        passwords: 密碼列表，用於解密受保護的 PDF

    Returns:
        提取的文字內容

    Raises:
        PDFExtractionError: PDF 開啟失敗、密碼錯誤或文字提取失敗時拋出
    """
    if passwords is None:
        passwords = []

    try:
        # 開啟 PDF 文件
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise PDFExtractionError(f"無法開啟 PDF 文件: {str(e)}")

    try:
        # 檢查是否需要密碼
        if doc.needs_pass:
            # 依序嘗試密碼列表
            authenticated = False
            for pwd in passwords:
                if doc.authenticate(pwd):
                    authenticated = True
                    break

            # 若所有密碼都失敗
            if not authenticated:
                raise PDFExtractionError("PDF 密碼驗證失敗：提供的密碼均不正確")

        # 提取所有頁面的文字
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            text_parts.append(page_text)

        # 合併所有頁面的文字
        full_text = "\n".join(text_parts)

        return full_text

    finally:
        # 確保文件被正確關閉
        doc.close()


def extract_text_from_base64_pdf(pdf_base64: str, passwords: Optional[list[str]] = None) -> str:
    """
    從 Base64 編碼的 PDF 中提取文字

    這是一個便利函數，結合了 Base64 解碼和文字提取。

    Args:
        pdf_base64: Base64 編碼的 PDF 字串
        passwords: 密碼列表，用於解密受保護的 PDF

    Returns:
        提取的文字內容

    Raises:
        PDFExtractionError: 處理過程中發生錯誤時拋出
    """
    pdf_bytes = decode_base64_pdf(pdf_base64)
    return extract_text_from_pdf(pdf_bytes, passwords)
