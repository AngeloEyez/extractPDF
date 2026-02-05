# PDF 轉文字 API 服務

將 PDF 檔案轉換為純文字的 RESTful API 服務，支援密碼保護的 PDF。

## 功能特點

- 支援 Base64 編碼的 PDF 輸入
- 支援密碼保護的 PDF（RC4/AES 加密）
- 支援多密碼嘗試
- 自動產生 API 文件（Swagger UI）

---

## 快速部署（Debian 12+）

### 一鍵安裝

```bash
# 下載並執行安裝腳本
curl -sSL https://raw.githubusercontent.com/AngeloEyez/extractPDF/main/scripts/install.sh | sudo bash
```

或手動安裝：

```bash
git clone https://github.com/AngeloEyez/extractPDF.git
cd extractPDF
sudo bash scripts/install.sh
```

### 更新服務

```bash
sudo bash /opt/extractpdf/scripts/update.sh
```

### 移除服務

```bash
# 下載並執行移除腳本
curl -sSL https://raw.githubusercontent.com/AngeloEyez/extractPDF/main/scripts/uninstall.sh | sudo bash
```

### 服務管理

```bash
# 查看狀態
sudo systemctl status extractpdf

# 重啟服務
sudo systemctl restart extractpdf

# 查看日誌
sudo journalctl -u extractpdf -f
```

---

## 本機開發

### 安裝

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

### 執行

```bash
# 開發模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生產模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 測試

```bash
# 設定測試密碼環境變數
export PDF_TEST_PASSWORD="your_test_password"

# 執行測試
pytest tests/ -v
```

---

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

---

## 工具列表

### PDF 解密工具 (`scripts/decrypt_pdf.py`)

如果您知道 PDF 的 User Password，但想移除密碼保護（包含 Admin Password 限制），可使用此工具：

```bash
# 基本用法
python scripts/decrypt_pdf.py <輸入PDF> <User密碼>

# 範例
python scripts/decrypt_pdf.py input.pdf F124599126
# 輸出: input_decrypted.pdf (無密碼保護)
```

---

## 專案結構

```
extractPDF/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用程式入口
│   ├── routers/
│   │   └── pdf.py           # PDF API 路由
│   └── services/
│       └── pdf_extractor.py # PDF 處理核心邏輯
├── scripts/
│   ├── install.sh           # Debian 安裝腳本
│   └── update.sh            # 更新腳本
├── tests/
│   └── test_pdf_extractor.py
├── requirements.txt
└── README.md
```
