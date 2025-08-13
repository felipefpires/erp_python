#!/bin/bash

# Script de Gerenciamento - Sistema ERP
# Uso: ./manage.sh [comando]

APP_NAME="erp-system"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="erp-system"
USER_NAME="erp"
BACKUP_DIR="$APP_DIR/backups"
LOG_DIR="$APP_DIR/logs"

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
    echo "  update-git - Atualizar do GitHub"
    echo "  shell     - Abrir shell Python"
    echo "  migrate   - Executar migrações do banco"
    echo "  health    - Verificar saúde do sistema"
    echo "  clean     - Limpar logs e backups antigos"
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
    if command -v netstat &> /dev/null; then
        sudo netstat -tlnp | grep -E "(80|443|5000)" || echo "Nenhuma porta encontrada"
    else
        echo "netstat não disponível"
    fi
    echo ""
    echo "=== Socket ==="
    ls -la $APP_DIR/$SERVICE_NAME.sock 2>/dev/null || echo "Socket não encontrado"
}

show_logs() {
    log "📋 Logs do Sistema ERP..."
    echo ""
    echo "=== Logs de Acesso ==="
    if [ -f "$LOG_DIR/access.log" ]; then
        tail -20 $LOG_DIR/access.log
    else
        echo "Arquivo de log não encontrado"
    fi
    echo ""
    echo "=== Logs de Erro ==="
    if [ -f "$LOG_DIR/error.log" ]; then
        tail -20 $LOG_DIR/error.log
    else
        echo "Arquivo de log não encontrado"
    fi
    echo ""
    echo "=== Logs do Supervisor ==="
    if [ -f "$LOG_DIR/supervisor_err.log" ]; then
        tail -10 $LOG_DIR/supervisor_err.log
    else
        echo "Arquivo de log não encontrado"
    fi
    echo ""
    echo "=== Logs do Nginx ==="
    sudo tail -10 /var/log/nginx/error.log
}

backup_database() {
    log "💾 Fazendo backup do banco de dados..."
    BACKUP_FILE="erp_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    sudo -u $USER_NAME mkdir -p $BACKUP_DIR
    sudo -u $USER_NAME tar -czf $BACKUP_DIR/$BACKUP_FILE -C $APP_DIR instance/ uploads/ .env 2>/dev/null || true
    
    log "✅ Backup criado: $BACKUP_FILE"
    
    # Manter apenas os últimos 10 backups
    sudo -u $USER_NAME find $BACKUP_DIR -name "erp_backup_*.tar.gz" -type f -printf '%T@ %p\n' | sort -n | head -n -10 | cut -d' ' -f2- | xargs -r rm
}

update_system() {
    log "🔄 Atualizando Sistema ERP..."
    
    # Fazer backup antes da atualização
    backup_database
    
    # Parar serviços
    stop_service
    
    # Atualizar dependências
    sudo -u $USER_NAME $VENV_DIR/bin/pip install -r $APP_DIR/requirements.txt
    
    # Executar migrações
    cd $APP_DIR
    sudo -u $USER_NAME $VENV_DIR/bin/python init_db.py
    
    # Reiniciar serviços
    start_service
    
    log "✅ Sistema atualizado!"
}

update_from_git() {
    log "🔄 Atualizando do GitHub..."
    
    # Verificar se é um repositório git
    if [ ! -d "$APP_DIR/.git" ]; then
        error "Diretório não é um repositório git"
        return 1
    fi
    
    # Fazer backup antes da atualização
    backup_database
    
    # Parar serviços
    stop_service
    
    # Atualizar código do GitHub
    cd $APP_DIR
    sudo -u $USER_NAME git fetch origin
    sudo -u $USER_NAME git reset --hard origin/main
    
    # Atualizar dependências
    sudo -u $USER_NAME $VENV_DIR/bin/pip install -r requirements.txt
    
    # Executar migrações
    sudo -u $USER_NAME $VENV_DIR/bin/python init_db.py
    
    # Configurar permissões
    sudo chown -R $USER_NAME:$USER_NAME $APP_DIR
    
    # Reiniciar serviços
    start_service
    
    log "✅ Sistema atualizado do GitHub!"
}

open_shell() {
    log "🐍 Abrindo shell Python..."
    cd $APP_DIR
    sudo -u $USER_NAME $VENV_DIR/bin/python
}

run_migrations() {
    log "🗄️ Executando migrações do banco..."
    cd $APP_DIR
    sudo -u $USER_NAME $VENV_DIR/bin/python init_db.py
    log "✅ Migrações executadas!"
}

check_health() {
    log "🏥 Verificando saúde do sistema..."
    
    # Verificar se os serviços estão rodando
    if sudo supervisorctl status $SERVICE_NAME | grep -q "RUNNING"; then
        echo "✅ Supervisor: OK"
    else
        echo "❌ Supervisor: ERRO"
    fi
    
    if sudo systemctl is-active --quiet nginx; then
        echo "✅ Nginx: OK"
    else
        echo "❌ Nginx: ERRO"
    fi
    
    # Verificar socket
    if [ -S "$APP_DIR/$SERVICE_NAME.sock" ]; then
        echo "✅ Socket: OK"
    else
        echo "❌ Socket: ERRO"
    fi
    
    # Testar aplicação
    if curl -s http://localhost/health > /dev/null; then
        echo "✅ Aplicação: OK"
    else
        echo "❌ Aplicação: ERRO"
    fi
    
    # Verificar espaço em disco
    DISK_USAGE=$(df $APP_DIR | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -lt 90 ]; then
        echo "✅ Disco: OK ($DISK_USAGE%)"
    else
        echo "⚠️ Disco: ATENÇÃO ($DISK_USAGE%)"
    fi
}

cleanup_system() {
    log "🧹 Limpando sistema..."
    
    # Limpar logs antigos (mais de 30 dias)
    sudo find $LOG_DIR -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
    
    # Limpar backups antigos (mais de 7 dias)
    sudo find $BACKUP_DIR -name "erp_backup_*.tar.gz" -type f -mtime +7 -delete 2>/dev/null || true
    
    # Limpar cache do pip
    sudo -u $USER_NAME $VENV_DIR/bin/pip cache purge
    
    log "✅ Limpeza concluída!"
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
    update-git)
        update_from_git
        ;;
    shell)
        open_shell
        ;;
    migrate)
        run_migrations
        ;;
    health)
        check_health
        ;;
    clean)
        cleanup_system
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
