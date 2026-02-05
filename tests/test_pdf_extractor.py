"""
PDF 文字提取服務測試模組

測試 PDF 解密和文字提取功能，包含兩種不同加密方式的 PDF 檔案。
"""

import os
import base64
from pathlib import Path

import pytest

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent

# 測試 PDF 檔案路徑
TEST_PDF_DIR = PROJECT_ROOT / "test"
TEST_PDF_1 = TEST_PDF_DIR / "84_2143504-20603_20603.PDF"
TEST_PDF_2 = TEST_PDF_DIR / "收益分配通知書.pdf"

# 測試密碼（從環境變數讀取，避免硬編碼）
TEST_PASSWORD = os.environ.get("PDF_TEST_PASSWORD", "")


def load_pdf_as_base64(file_path: Path) -> str:
    """
    讀取 PDF 檔案並轉換為 Base64 編碼

    Args:
        file_path: PDF 檔案路徑

    Returns:
        Base64 編碼的字串
    """
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


class TestPDFExtractor:
    """PDF 提取器測試類別"""

    def test_extract_pdf_1(self):
        """測試第一個 PDF 檔案（84_2143504-20603_20603.PDF）"""
        from app.services.pdf_extractor import extract_text_from_base64_pdf

        # 確認測試檔案存在
        assert TEST_PDF_1.exists(), f"測試檔案不存在: {TEST_PDF_1}"

        # 讀取 PDF 並轉換為 Base64
        pdf_base64 = load_pdf_as_base64(TEST_PDF_1)

        # 提取文字
        text = extract_text_from_base64_pdf(pdf_base64, [TEST_PASSWORD])

        # 驗證結果
        assert text is not None, "提取的文字不應為 None"
        assert len(text) > 0, "提取的文字不應為空"
        print(f"\n[PDF 1] 提取文字長度: {len(text)} 字元")
        print(f"[PDF 1] 文字預覽: {text[:200]}...")

    def test_extract_pdf_2(self):
        """測試第二個 PDF 檔案（收益分配通知書.pdf）"""
        from app.services.pdf_extractor import extract_text_from_base64_pdf

        # 確認測試檔案存在
        assert TEST_PDF_2.exists(), f"測試檔案不存在: {TEST_PDF_2}"

        # 讀取 PDF 並轉換為 Base64
        pdf_base64 = load_pdf_as_base64(TEST_PDF_2)

        # 提取文字
        text = extract_text_from_base64_pdf(pdf_base64, [TEST_PASSWORD])

        # 驗證結果
        assert text is not None, "提取的文字不應為 None"
        assert len(text) > 0, "提取的文字不應為空"
        print(f"\n[PDF 2] 提取文字長度: {len(text)} 字元")
        print(f"[PDF 2] 文字預覽: {text[:200]}...")

    def test_wrong_password(self):
        """測試錯誤密碼的錯誤處理"""
        from app.services.pdf_extractor import (
            extract_text_from_base64_pdf,
            PDFExtractionError
        )

        # 確認測試檔案存在
        assert TEST_PDF_1.exists(), f"測試檔案不存在: {TEST_PDF_1}"

        # 讀取 PDF 並轉換為 Base64
        pdf_base64 = load_pdf_as_base64(TEST_PDF_1)

        # 使用錯誤密碼應該拋出例外
        with pytest.raises(PDFExtractionError) as exc_info:
            extract_text_from_base64_pdf(pdf_base64, ["wrong_password"])

        assert "密碼" in str(exc_info.value), "錯誤訊息應包含密碼相關描述"
        print(f"\n[錯誤密碼測試] 例外訊息: {exc_info.value}")

    def test_empty_password_list(self):
        """測試空密碼列表的錯誤處理"""
        from app.services.pdf_extractor import (
            extract_text_from_base64_pdf,
            PDFExtractionError
        )

        # 確認測試檔案存在
        assert TEST_PDF_1.exists(), f"測試檔案不存在: {TEST_PDF_1}"

        # 讀取 PDF 並轉換為 Base64
        pdf_base64 = load_pdf_as_base64(TEST_PDF_1)

        # 空密碼列表應該拋出例外
        with pytest.raises(PDFExtractionError) as exc_info:
            extract_text_from_base64_pdf(pdf_base64, [])

        assert "密碼" in str(exc_info.value), "錯誤訊息應包含密碼相關描述"
        print(f"\n[空密碼測試] 例外訊息: {exc_info.value}")


class TestAPIEndpoint:
    """API 端點測試類別"""

    def test_pdf_to_text_endpoint(self):
        """測試 /pdf/toText API 端點"""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # 確認測試檔案存在
        assert TEST_PDF_1.exists(), f"測試檔案不存在: {TEST_PDF_1}"

        # 準備請求資料
        pdf_base64 = load_pdf_as_base64(TEST_PDF_1)
        payload = {
            "pdf": pdf_base64,
            "passwords": [TEST_PASSWORD]
        }

        # 發送 POST 請求
        response = client.post("/pdf/toText", json=payload)

        # 驗證回應
        assert response.status_code == 200, f"API 回應錯誤: {response.text}"

        result = response.json()
        assert "text" in result, "回應應包含 'text' 欄位"
        assert len(result["text"]) > 0, "提取的文字不應為空"
        print(f"\n[API 測試] 提取文字長度: {len(result['text'])} 字元")

    def test_pdf_to_text_wrong_password(self):
        """測試 API 端點的錯誤密碼處理"""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # 確認測試檔案存在
        assert TEST_PDF_1.exists(), f"測試檔案不存在: {TEST_PDF_1}"

        # 準備請求資料（錯誤密碼）
        pdf_base64 = load_pdf_as_base64(TEST_PDF_1)
        payload = {
            "pdf": pdf_base64,
            "passwords": ["wrong_password"]
        }

        # 發送 POST 請求
        response = client.post("/pdf/toText", json=payload)

        # 應該回傳 400 錯誤
        assert response.status_code == 400, f"預期 400 錯誤，實際: {response.status_code}"
        print(f"\n[API 錯誤測試] 回應: {response.json()}")

    def test_health_check(self):
        """測試健康檢查端點"""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
