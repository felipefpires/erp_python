#!/bin/bash

# Script de Gerenciamento - Sistema ERP
# Uso: ./manage.sh [comando]

APP_NAME="erp-system"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="erp-system"
USER_NAME="erp"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERRO] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[AVISO] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

show_help() {
    echo "Sistema ERP - Script de Gerenciamento"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  start     - Iniciar o sistema"
    echo "  stop      - Parar o sistema"
    echo "  restart   - Reiniciar o sistema"
    echo "  status    - Verificar status"
    echo "  logs      - Ver logs"
    echo "  backup    - Fazer backup do banco"
    echo "  update    - Atualizar código e dependências"
    echo "  shell     - Abrir shell Python"
    echo "  migrate   - Executar migrações do banco"
    echo "  help      - Mostrar esta ajuda"
}

start_service() {
    log "🚀 Iniciando Sistema ERP..."
    sudo supervisorctl start $SERVICE_NAME
    sudo systemctl start nginx
    log "✅ Sistema iniciado!"
}

stop_service() {
    log "🛑 Parando Sistema ERP..."
    sudo supervisorctl stop $SERVICE_NAME
    sudo systemctl stop nginx
    log "✅ Sistema parado!"
}

restart_service() {
    log "🔄 Reiniciando Sistema ERP..."
    sudo supervisorctl restart $SERVICE_NAME
    sudo systemctl reload nginx
    log "✅ Sistema reiniciado!"
}

show_status() {
    log "📊 Status do Sistema ERP..."
    echo ""
    echo "=== Supervisor ==="
    sudo supervisorctl status $SERVICE_NAME
    echo ""
    echo "=== Nginx ==="
    sudo systemctl status nginx --no-pager -l
    echo ""
    echo "=== Processos ==="
    ps aux | grep -E "(gunicorn|nginx)" | grep -v grep
    echo ""
    echo "=== Portas ==="
    sudo netstat -tlnp | grep -E "(80|443|5000)"
}

show_logs() {
    log "📋 Logs do Sistema ERP..."
    echo ""
    echo "=== Logs de Acesso ==="
    tail -20 $APP_DIR/logs/access.log
    echo ""
    echo "=== Logs de Erro ==="
    tail -20 $APP_DIR/logs/error.log
    echo ""
    echo "=== Logs do Supervisor ==="
    tail -10 $APP_DIR/logs/supervisor_err.log
    echo ""
    echo "=== Logs do Nginx ==="
    sudo tail -10 /var/log/nginx/error.log
}

backup_database() {
    log "💾 Fazendo backup do banco de dados..."
    BACKUP_DIR="$APP_DIR/backups"
    BACKUP_FILE="erp_backup_$(date +%Y%m%d_%H%M%S).db"
    
    sudo -u $USER_NAME mkdir -p $BACKUP_DIR
    sudo -u $USER_NAME cp $APP_DIR/instance/erp.db $BACKUP_DIR/$BACKUP_FILE
    
    log "✅ Backup criado: $BACKUP_DIR/$BACKUP_FILE"
    
    # Manter apenas os últimos 10 backups
    sudo -u $USER_NAME find $BACKUP_DIR -name "erp_backup_*.db" -type f -printf '%T@ %p\n' | sort -n | head -n -10 | cut -d' ' -f2- | xargs -r rm
}

update_system() {
    log "🔄 Atualizando Sistema ERP..."
    
    # Fazer backup antes da atualização
    backup_database
    
    # Parar serviços
    stop_service
    
    # Atualizar código (assumindo que está em um repositório git)
    cd $APP_DIR
    if [ -d ".git" ]; then
        sudo -u $USER_NAME git pull origin main
    else
        warning "Diretório não é um repositório git. Atualize manualmente."
    fi
    
    # Atualizar dependências
    sudo -u $USER_NAME $VENV_DIR/bin/pip install -r requirements.txt
    
    # Executar migrações
    sudo -u $USER_NAME $VENV_DIR/bin/flask db upgrade
    
    # Reiniciar serviços
    start_service
    
    log "✅ Sistema atualizado!"
}

open_shell() {
    log "🐍 Abrindo shell Python..."
    cd $APP_DIR
    sudo -u $USER_NAME $VENV_DIR/bin/python
}

run_migrations() {
    log "🗄️ Executando migrações do banco..."
    cd $APP_DIR
    sudo -u $USER_NAME $VENV_DIR/bin/flask db upgrade
    log "✅ Migrações executadas!"
}

# Verificar se o comando foi fornecido
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# Executar comando
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    backup)
        backup_database
        ;;
    update)
        update_system
        ;;
    shell)
        open_shell
        ;;
    migrate)
        run_migrations
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Comando desconhecido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
