#!/bin/bash
# ============================================================
# PDF 轉文字 API 服務 - 移除腳本
# ============================================================
# 此腳本會移除已安裝的 PDF 轉文字 API 服務與相關檔案
# 執行方式: sudo bash uninstall.sh
# ============================================================

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置變數（需與 install.sh 一致）
APP_NAME="extractpdf"
APP_USER="extractpdf"
APP_DIR="/opt/extractpdf"

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

# 確認移除
confirm_uninstall() {
    echo -e "${RED}警告：這將完全移除 PDF 轉文字 API 服務與所有資料！${NC}"
    echo "包含："
    echo "  - 停止並移除 systemd 服務 ($APP_NAME)"
    echo "  - 刪除應用程式目錄 ($APP_DIR)"
    echo "  - 刪除應用程式使用者 ($APP_USER)"
    echo ""
    read -p "確定要繼續嗎？(y/N) " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        info "已取消移除"
        exit 0
    fi
}

# 停止並移除服務
remove_service() {
    info "停止並移除服務..."
    if systemctl is-active --quiet ${APP_NAME}; then
        systemctl stop ${APP_NAME}
    fi
    
    if systemctl is-enabled --quiet ${APP_NAME}; then
        systemctl disable ${APP_NAME}
    fi
    
    if [ -f "/etc/systemd/system/${APP_NAME}.service" ]; then
        rm "/etc/systemd/system/${APP_NAME}.service"
        systemctl daemon-reload
        info "服務設定檔已移除"
    else
        warn "找不到服務設定檔"
    fi
}

# 移除檔案
remove_files() {
    if [ -d "$APP_DIR" ]; then
        info "移除應用程式目錄..."
        rm -rf "$APP_DIR"
    else
        warn "找不到應用程式目錄 $APP_DIR"
    fi
}

# 移除使用者
remove_user() {
    if id "$APP_USER" &>/dev/null; then
        info "移除應用程式使用者..."
        userdel "$APP_USER" || warn "無法移除使用者（可能由其他程序使用中）"
    else
        warn "使用者 $APP_USER 不存在"
    fi
}

# 顯示結果
show_result() {
    echo ""
    echo "============================================================"
    echo -e "${GREEN}移除完成！${NC}"
    echo "============================================================"
    echo "注意：Tesseract OCR 等系統套件未被移除，若不再需要請手動執行："
    echo "sudo apt-get remove tesseract-ocr tesseract-ocr-chi-tra tesseract-ocr-chi-sim"
    echo ""
}

# 主程式
main() {
    info "開始移除 PDF 轉文字 API 服務..."
    echo ""
    
    check_root
    confirm_uninstall
    remove_service
    remove_files
    remove_user
    show_result
}

main "$@"
