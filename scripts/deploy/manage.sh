#!/bin/bash

# Script de gerenciamento do ERP System em produção
# Uso: ./manage.sh [comando]

set -e

SERVICE_NAME="erp-system"
APP_DIR="/opt/erp-system"
BACKUP_DIR="/opt/backups/erp"

# Funções de utilidade
log() {
    echo -e "\033[0;32m[$(date +'%Y-%m-%d %H:%M:%S')] $1\033[0m"
}

error() {
    echo -e "\033[0;31m[ERRO] $1\033[0m"
    exit 1
}

warning() {
    echo -e "\033[1;33m[AVISO] $1\033[0m"
}

# Verificar se o serviço existe
check_service() {
    if [ ! -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
        error "Serviço $SERVICE_NAME não encontrado. Execute o setup primeiro."
    fi
}

# Comando: status
status() {
    log "📊 Status do Sistema ERP"
    echo "========================"
    
    # Status do serviço
    echo "🔧 Status do Serviço:"
    systemctl status $SERVICE_NAME --no-pager -l
    
    echo ""
    echo "🌐 Status do Nginx:"
    systemctl status nginx --no-pager -l
    
    echo ""
    echo "💾 Espaço em Disco:"
    df -h /opt/erp-system
    
    echo ""
    echo "📊 Uso de Memória:"
    free -h
    
    echo ""
    echo "🔗 Portas em Uso:"
    netstat -tlnp | grep -E ':(80|5000)'
}

# Comando: logs
logs() {
    log "📋 Logs do Sistema"
    echo "=================="
    
    echo "🔧 Logs do Serviço:"
    journalctl -u $SERVICE_NAME -n 50 --no-pager
    
    echo ""
    echo "🌐 Logs do Nginx:"
    tail -n 20 /var/log/nginx/error.log
}

# Comando: restart
restart() {
    log "🔄 Reiniciando Sistema ERP"
    echo "=========================="
    
    check_service
    
    systemctl restart $SERVICE_NAME
    systemctl restart nginx
    
    sleep 3
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        log "✅ Sistema reiniciado com sucesso!"
    else
        error "❌ Falha ao reiniciar o sistema"
    fi
}

# Comando: backup
backup() {
    log "💾 Criando Backup"
    echo "================="
    
    DATE=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/erp_manual_$DATE.db"
    
    mkdir -p $BACKUP_DIR
    
    if [ -f "$APP_DIR/instance/erp.db" ]; then
        cp "$APP_DIR/instance/erp.db" "$BACKUP_FILE"
        log "✅ Backup criado: $BACKUP_FILE"
        
        # Mostrar tamanho do backup
        SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo "📊 Tamanho: $SIZE"
    else
        error "❌ Arquivo de banco de dados não encontrado"
    fi
}

# Comando: restore
restore() {
    log "🔄 Restaurando Backup"
    echo "===================="
    
    if [ -z "$1" ]; then
        echo "📋 Backups disponíveis:"
        ls -la $BACKUP_DIR/*.db 2>/dev/null || echo "Nenhum backup encontrado"
        echo ""
        echo "Uso: $0 restore <arquivo_backup>"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        error "❌ Arquivo de backup não encontrado: $BACKUP_FILE"
    fi
    
    # Fazer backup antes da restauração
    backup
    
    # Parar serviço
    systemctl stop $SERVICE_NAME
    
    # Restaurar
    cp "$BACKUP_FILE" "$APP_DIR/instance/erp.db"
    
    # Reiniciar serviço
    systemctl start $SERVICE_NAME
    
    log "✅ Backup restaurado com sucesso!"
}

# Comando: update
update() {
    log "🔄 Atualizando Sistema"
    echo "====================="
    
    cd $APP_DIR
    
    # Fazer backup antes da atualização
    backup
    
    # Atualizar código
    git pull origin main
    
    # Atualizar dependências
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Reiniciar serviço
    restart
    
    log "✅ Sistema atualizado com sucesso!"
}

# Comando: health
health() {
    log "🏥 Verificação de Saúde"
    echo "======================"
    
    # Verificar se o serviço está rodando
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo "✅ Serviço ERP: ATIVO"
    else
        echo "❌ Serviço ERP: INATIVO"
    fi
    
    # Verificar se o Nginx está rodando
    if systemctl is-active --quiet nginx; then
        echo "✅ Nginx: ATIVO"
    else
        echo "❌ Nginx: INATIVO"
    fi
    
    # Verificar se a aplicação responde
    if curl -s http://localhost/ > /dev/null; then
        echo "✅ Aplicação Web: RESPONDENDO"
    else
        echo "❌ Aplicação Web: NÃO RESPONDE"
    fi
    
    # Verificar espaço em disco
    DISK_USAGE=$(df /opt/erp-system | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -lt 80 ]; then
        echo "✅ Espaço em Disco: OK ($DISK_USAGE%)"
    else
        echo "⚠️ Espaço em Disco: CRÍTICO ($DISK_USAGE%)"
    fi
    
    # Verificar memória
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$MEM_USAGE" -lt 80 ]; then
        echo "✅ Uso de Memória: OK ($MEM_USAGE%)"
    else
        echo "⚠️ Uso de Memória: CRÍTICO ($MEM_USAGE%)"
    fi
}

# Comando: clean
clean() {
    log "🧹 Limpeza do Sistema"
    echo "===================="
    
    # Limpar logs antigos
    journalctl --vacuum-time=7d
    
    # Limpar backups antigos (manter apenas 7 dias)
    find $BACKUP_DIR -name "*.db" -mtime +7 -delete 2>/dev/null || true
    
    # Limpar cache do pip
    cd $APP_DIR
    source venv/bin/activate
    pip cache purge
    
    log "✅ Limpeza concluída!"
}

# Comando: help
help() {
    echo "🔧 Gerenciador do Sistema ERP"
    echo "============================="
    echo ""
    echo "Comandos disponíveis:"
    echo "  status    - Mostrar status do sistema"
    echo "  logs      - Mostrar logs recentes"
    echo "  restart   - Reiniciar o sistema"
    echo "  backup    - Criar backup manual"
    echo "  restore   - Restaurar backup"
    echo "  update    - Atualizar sistema do GitHub"
    echo "  health    - Verificar saúde do sistema"
    echo "  clean     - Limpar logs e cache"
    echo "  help      - Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 status"
    echo "  $0 backup"
    echo "  $0 restore /opt/backups/erp/erp_20231201_120000.db"
}

# Verificar se o usuário é root
if [ "$EUID" -ne 0 ]; then
    error "Este script deve ser executado como root (use sudo)"
fi

# Processar comando
case "${1:-help}" in
    status)
        status
        ;;
    logs)
        logs
        ;;
    restart)
        restart
        ;;
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    update)
        update
        ;;
    health)
        health
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        help
        ;;
    *)
        error "Comando inválido: $1"
        help
        ;;
esac
