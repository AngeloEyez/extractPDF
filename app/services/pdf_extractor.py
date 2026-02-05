"""
PDF 文字提取服務模組

提供 PDF 解密和文字提取功能，支援多種加密方式（RC4/AES）。
當原生提取失敗（亂碼）時，自動回退到 OCR 處理。
"""

import base64
import re
import io
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


def is_valid_text(text: str, threshold: float = 0.3) -> bool:
    """
    檢查提取的文字是否有效（非亂碼）

    使用以下標準判斷：
    1. 排除替換字元 (U+FFFD)
    2. 檢查是否包含足夠的可讀字元（中文、英文、數字、常見標點）

    Args:
        text: 要檢查的文字
        threshold: 可讀字元比例門檻（預設 0.3 = 30%）

    Returns:
        True 表示文字有效，False 表示可能是亂碼
    """
    if not text or len(text.strip()) == 0:
        return False

    # 移除所有空白字元後計算
    cleaned = text.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
    if len(cleaned) == 0:
        return True  # 空內容視為有效

    # 可讀字元模式：中文、英文、數字、常見標點
    # \u4e00-\u9fff: 常用漢字
    # \u3000-\u303f: 中日韓標點
    # a-zA-Z0-9: 英數字
    readable_pattern = re.compile(r'[\u4e00-\u9fff\u3000-\u303fa-zA-Z0-9.,;:!?()（）、。，；：！？「」『』【】\-\s]')

    # 計算可讀字元數量
    readable_chars = len(readable_pattern.findall(cleaned))
    ratio = readable_chars / len(cleaned)

    return ratio >= threshold


def extract_text_native(doc: fitz.Document) -> str:
    """
    使用 PyMuPDF 原生方法提取文字

    Args:
        doc: 已開啟的 PDF 文件

    Returns:
        提取的文字內容
    """
    text_parts = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text()
        text_parts.append(page_text)

    return "\n".join(text_parts)


def extract_text_ocr(doc: fitz.Document, language: str = "chi_tra+chi_sim+eng") -> str:
    """
    使用 OCR 提取文字（適用於掃描 PDF 或字型編碼問題的 PDF）

    Args:
        doc: 已開啟的 PDF 文件
        language: Tesseract 語言設定（預設：繁體中文+簡體中文+英文）

    Returns:
        OCR 識別的文字內容
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise PDFExtractionError(
            "OCR 功能需要安裝 pytesseract 和 pillow。"
            "請執行: pip install pytesseract pillow"
        )

    text_parts = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        # 將頁面渲染為高解析度圖片（300 DPI）
        mat = fitz.Matrix(300 / 72, 300 / 72)  # 72 DPI -> 300 DPI
        pix = page.get_pixmap(matrix=mat)

        # 轉換為 PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))

        # 使用 Tesseract OCR
        try:
            page_text = pytesseract.image_to_string(img, lang=language)
            text_parts.append(page_text)
        except Exception as e:
            # OCR 失敗時記錄但繼續處理其他頁面
            text_parts.append(f"[OCR 失敗: {str(e)}]")

    return "\n".join(text_parts)


def extract_text_from_pdf(
    pdf_bytes: bytes,
    passwords: Optional[list[str]] = None,
    force_ocr: bool = False
) -> str:
    """
    從 PDF 位元組中提取文字

    支援密碼保護的 PDF 檔案。會依序嘗試提供的密碼列表，
    直到成功解密或所有密碼都嘗試失敗。

    當原生提取結果為亂碼時，自動嘗試 OCR。

    Args:
        pdf_bytes: PDF 檔案的位元組內容
        passwords: 密碼列表，用於解密受保護的 PDF
        force_ocr: 強制使用 OCR（跳過原生提取）

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

        # 如果強制 OCR，直接使用 OCR
        if force_ocr:
            return extract_text_ocr(doc)

        # 嘗試原生提取
        native_text = extract_text_native(doc)

        # 檢查提取結果是否有效
        if is_valid_text(native_text):
            return native_text

        # 原生提取結果為亂碼，嘗試 OCR
        try:
            ocr_text = extract_text_ocr(doc)
            if is_valid_text(ocr_text):
                return ocr_text
            else:
                # OCR 結果也不理想，回傳原生結果
                return native_text
        except PDFExtractionError:
            # OCR 不可用，回傳原生結果
            return native_text

    finally:
        # 確保文件被正確關閉
        doc.close()


def extract_text_from_base64_pdf(
    pdf_base64: str,
    passwords: Optional[list[str]] = None,
    force_ocr: bool = False
) -> str:
    """
    從 Base64 編碼的 PDF 中提取文字

    這是一個便利函數，結合了 Base64 解碼和文字提取。

    Args:
        pdf_base64: Base64 編碼的 PDF 字串
        passwords: 密碼列表，用於解密受保護的 PDF
        force_ocr: 強制使用 OCR（跳過原生提取）

    Returns:
        提取的文字內容

    Raises:
        PDFExtractionError: 處理過程中發生錯誤時拋出
    """
    pdf_bytes = decode_base64_pdf(pdf_base64)
    return extract_text_from_pdf(pdf_bytes, passwords, force_ocr)
