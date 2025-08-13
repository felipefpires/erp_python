#!/bin/bash

# Script de Instalação Limpa - Sistema ERP
# Remove tudo e instala do zero
# Uso: ./clean-install.sh [GITHUB_REPO_URL]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERRO] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[AVISO] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   error "Este script não deve ser executado como root"
fi

# GitHub repository (pode ser passado como parâmetro)
GITHUB_REPO=${1:-"https://github.com/felipefpires/erp_python.git"}

log "🧹 INSTALAÇÃO LIMPA - Sistema ERP"
log "📦 Repositório: $GITHUB_REPO"
echo ""

# Confirmar instalação limpa
warning "⚠️ ATENÇÃO: Este script irá REMOVER completamente o sistema atual!"
read -p "Deseja continuar? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Instalação cancelada"
    exit 0
fi

# Função para fazer backup antes de remover
backup_existing() {
    if [ -d "/opt/erp-system" ] && [ -f "/opt/erp-system/instance/erp.db" ]; then
        log "💾 Fazendo backup do sistema atual..."
        BACKUP_FILE="erp_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
        sudo tar -czf "/tmp/$BACKUP_FILE" -C /opt/erp-system instance/ uploads/ .env 2>/dev/null || true
        log "✅ Backup criado: /tmp/$BACKUP_FILE"
    fi
}

# Função para limpar completamente
cleanup_complete() {
    log "🧹 Removendo sistema atual..."
    
    # Parar serviços
    sudo systemctl stop nginx 2>/dev/null || true
    sudo supervisorctl stop erp-system 2>/dev/null || true
    
    # Remover configurações do Nginx
    sudo rm -f /etc/nginx/sites-enabled/*
    sudo rm -f /etc/nginx/sites-available/erp-system
    
    # Remover configurações do Supervisor
    sudo rm -f /etc/supervisor/conf.d/erp-system.conf
    
    # Remover diretório da aplicação
    sudo rm -rf /opt/erp-system
    
    # Remover usuário erp
    sudo userdel -r erp 2>/dev/null || true
    
    # Remover script de gerenciamento
    sudo rm -f /usr/local/bin/erp-manage
    
    # Limpar logs
    sudo rm -f /var/log/nginx/erp_*
    
    log "✅ Sistema removido completamente"
}

# Verificar conectividade
log "🌐 Verificando conectividade..."
if ! ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    error "Sem conectividade com a internet"
fi

# Fazer backup antes de remover
backup_existing

# Limpar completamente
cleanup_complete

# Atualizar sistema
log "📋 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Remover Nginx e Supervisor se existirem
log "🗑️ Removendo instalações antigas..."
sudo apt remove --purge nginx nginx-common nginx-full supervisor -y
sudo apt autoremove -y

# Instalar dependências essenciais
log "📦 Instalando dependências do sistema..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git curl wget net-tools

# Baixar código do GitHub
log "📥 Baixando código do GitHub..."
cd /tmp
sudo rm -rf erp-system-temp
sudo rm -rf erp_python
git clone $GITHUB_REPO erp-system-temp

if [ ! -d "erp-system-temp" ]; then
    error "Falha ao baixar código do GitHub"
fi

# Executar script de deploy
log "🔧 Executando deploy limpo..."
cd erp-system-temp
chmod +x scripts/deploy/deploy.sh
./scripts/deploy/deploy.sh $GITHUB_REPO

# Verificar instalação
log "✅ Verificando instalação..."
sleep 5

# Testar aplicação
if curl -s http://localhost/health > /dev/null; then
    log "🎉 Instalação limpa concluída com sucesso!"
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo ""
    echo "=========================================="
    echo "🚀 SISTEMA ERP INSTALADO DO ZERO!"
    echo "=========================================="
    echo "🌐 Acesse: http://$SERVER_IP"
    echo "🔧 Gerenciar: erp-manage status"
    echo "📁 Logs: /opt/erp-system/logs/"
    echo "💾 Backups: /opt/erp-system/backups/"
    echo "=========================================="
    echo ""
    log "📚 Comandos úteis:"
    echo "  erp-manage status    - Ver status"
    echo "  erp-manage logs      - Ver logs"
    echo "  erp-manage health    - Verificar saúde"
    echo "  erp-manage update-git - Atualizar do GitHub"
    echo "  erp-manage backup    - Fazer backup"
    echo ""
    
    # Restaurar backup se existir
    if [ -f "/tmp/erp_backup_$(date +%Y%m%d)*.tar.gz" ]; then
        warning "⚠️ Backup encontrado. Para restaurar dados:"
        echo "  sudo tar -xzf /tmp/erp_backup_*.tar.gz -C /opt/erp-system/"
        echo "  erp-manage restart"
    fi
else
    warning "⚠️ Aplicação pode não estar respondendo ainda"
    log "Verifique os logs: erp-manage logs"
fi
