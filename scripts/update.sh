#!/bin/bash
# ============================================================
# PDF 轉文字 API 服務 - 更新腳本
# ============================================================
# 此腳本會更新已安裝的 PDF 轉文字 API 服務
# 執行方式: sudo bash update.sh
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

# 檢查安裝目錄
check_installation() {
    if [ ! -d "$APP_DIR" ]; then
        error "找不到安裝目錄 $APP_DIR，請先執行 install.sh"
    fi
}

# 停止服務
stop_service() {
    info "停止服務..."
    systemctl stop ${APP_NAME} || warn "服務未在執行"
}

# 更新程式碼
update_code() {
    info "更新程式碼..."
    cd "$APP_DIR"
    
    # 解決 Git dubious ownership 問題 (因為腳本以 root 執行但目錄屬於 extractpdf)
    git config --global --add safe.directory "$APP_DIR"
    
    # 保存本地修改（如果有）
    git stash --quiet 2>/dev/null || true
    
    # 拉取最新程式碼
    git fetch origin
    git reset --hard origin/main
    
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    
    info "程式碼已更新至最新版本"
}

# 更新 Python 依賴
update_dependencies() {
    info "更新 Python 依賴..."
    cd "$APP_DIR"
    
    sudo -u "$APP_USER" ./venv/bin/pip install --upgrade pip -q
    sudo -u "$APP_USER" ./venv/bin/pip install -r requirements.txt -q --upgrade
    
    info "依賴更新完成"
}

# 重新載入並啟動服務
restart_service() {
    info "重新啟動服務..."
    
    # 重新載入 systemd（以防服務檔案有更新）
    systemctl daemon-reload
    
    # 啟動服務
    systemctl start ${APP_NAME}
    
    # 等待服務啟動
    sleep 2
    
    # 檢查服務狀態
    if systemctl is-active --quiet ${APP_NAME}; then
        info "服務已成功啟動"
    else
        error "服務啟動失敗，請檢查日誌: journalctl -u ${APP_NAME}"
    fi
}

# 顯示更新結果
show_result() {
    echo ""
    echo "============================================================"
    echo -e "${GREEN}更新完成！${NC}"
    echo "============================================================"
    echo ""
    echo "目前版本："
    cd "$APP_DIR"
    git log -1 --format="  提交: %h%n  日期: %ci%n  訊息: %s"
    echo ""
    echo "查看日誌: sudo journalctl -u ${APP_NAME} -f"
    echo ""
}

# 主程式
main() {
    info "開始更新 PDF 轉文字 API 服務..."
    echo ""
    
    check_root
    check_installation
    stop_service
    update_code
    update_dependencies
    restart_service
    show_result
}

main "$@"
