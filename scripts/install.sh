#!/bin/bash
# ============================================================
# PDF 轉文字 API 服務 - Debian 12+ 安裝腳本
# ============================================================
# 此腳本會在 Debian 12+ 系統上安裝並配置 PDF 轉文字 API 服務
# 執行方式: sudo bash install.sh
# ============================================================

set -e  # 發生錯誤時立即停止

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置變數
APP_NAME="extractpdf"
APP_USER="extractpdf"
APP_DIR="/opt/extractpdf"
REPO_URL="https://github.com/AngeloEyez/extractPDF.git"
SERVICE_PORT=8000

# 輸出函數
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# 檢查是否為 root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "請使用 sudo 執行此腳本"
    fi
}

# 安裝系統依賴
install_dependencies() {
    info "更新系統套件..."
    apt-get update -qq

    info "安裝必要套件..."
    apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        git \
        curl \
        > /dev/null

    info "系統依賴安裝完成"
}

# 建立應用程式使用者
create_user() {
    if id "$APP_USER" &>/dev/null; then
        info "使用者 $APP_USER 已存在"
    else
        info "建立使用者 $APP_USER..."
        useradd --system --shell /bin/bash --home-dir "$APP_DIR" "$APP_USER"
    fi
}

# 複製應用程式
clone_app() {
    if [ -d "$APP_DIR" ]; then
        warn "目錄 $APP_DIR 已存在，將進行更新..."
        cd "$APP_DIR"
        git fetch origin
        git reset --hard origin/main
    else
        info "複製專案到 $APP_DIR..."
        git clone "$REPO_URL" "$APP_DIR"
    fi

    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
}

# 建立 Python 虛擬環境並安裝依賴
setup_python() {
    info "建立 Python 虛擬環境..."
    cd "$APP_DIR"
    
    sudo -u "$APP_USER" python3 -m venv venv
    
    info "安裝 Python 依賴..."
    sudo -u "$APP_USER" ./venv/bin/pip install --upgrade pip -q
    sudo -u "$APP_USER" ./venv/bin/pip install -r requirements.txt -q
    
    info "Python 環境設定完成"
}

# 建立 systemd 服務
create_service() {
    info "建立 systemd 服務..."
    
    cat > /etc/systemd/system/${APP_NAME}.service << EOF
[Unit]
Description=PDF 轉文字 API 服務
After=network.target

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_PORT}
Restart=always
RestartSec=5

# 安全性設定
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    # 重新載入 systemd
    systemctl daemon-reload
    
    # 啟用並啟動服務
    systemctl enable ${APP_NAME}
    systemctl start ${APP_NAME}
    
    info "服務已啟動"
}

# 顯示安裝結果
show_result() {
    echo ""
    echo "============================================================"
    echo -e "${GREEN}安裝完成！${NC}"
    echo "============================================================"
    echo ""
    echo "服務資訊："
    echo "  - 服務名稱: ${APP_NAME}"
    echo "  - 安裝目錄: ${APP_DIR}"
    echo "  - 服務埠號: ${SERVICE_PORT}"
    echo "  - API 端點: http://localhost:${SERVICE_PORT}/pdf/toText"
    echo "  - API 文件: http://localhost:${SERVICE_PORT}/docs"
    echo ""
    echo "常用指令："
    echo "  - 查看狀態: sudo systemctl status ${APP_NAME}"
    echo "  - 重啟服務: sudo systemctl restart ${APP_NAME}"
    echo "  - 查看日誌: sudo journalctl -u ${APP_NAME} -f"
    echo "  - 更新服務: sudo bash ${APP_DIR}/scripts/update.sh"
    echo ""
}

# 主程式
main() {
    info "開始安裝 PDF 轉文字 API 服務..."
    echo ""
    
    check_root
    install_dependencies
    create_user
    clone_app
    setup_python
    create_service
    show_result
}

main "$@"
