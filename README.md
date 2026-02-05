# PDF 轉文字 API 服務

將 PDF 檔案轉換為純文字的 RESTful API 服務，支援密碼保護的 PDF。

## 功能特點

- 支援 Base64 編碼的 PDF 輸入
- 支援密碼保護的 PDF（RC4/AES 加密）
- 支援多密碼嘗試
- 自動產生 API 文件（Swagger UI）

## 安裝

```bash
# 建立虛擬環境
python -m venv venv

# 啟用虛擬環境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

## 執行

```bash
# 開發模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生產模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 使用

### POST /pdf/toText

將 PDF 轉換為純文字。

**請求格式：**
```json
{
  "pdf": "Base64 編碼的 PDF 內容",
  "passwords": ["密碼1", "密碼2"]
}
```

**回應格式：**
```json
{
  "text": "提取的文字內容"
}
```

### API 文件

啟動服務後，可透過以下網址查看 API 文件：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 測試

```bash
# 執行所有測試
pytest tests/ -v

# 執行特定測試
pytest tests/test_pdf_extractor.py -v
```

## 專案結構

```
extractPDF/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用程式入口
│   ├── routers/
│   │   ├── __init__.py
│   │   └── pdf.py           # PDF API 路由
│   └── services/
│       ├── __init__.py
│       └── pdf_extractor.py # PDF 處理核心邏輯
├── tests/
│   ├── __init__.py
│   └── test_pdf_extractor.py
├── test/                     # 測試 PDF 檔案
├── requirements.txt
└── README.md
```
