#!/bin/bash

# Script de Instalação Inicial - Sistema ERP
# Execute este script no servidor Ubuntu para instalar o sistema pela primeira vez
# Uso: ./install.sh [GITHUB_REPO_URL]

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
GITHUB_REPO=${1:-"https://github.com/seu-usuario/erp-project.git"}

log "🚀 Instalação Inicial do Sistema ERP"
log "📦 Repositório: $GITHUB_REPO"
echo ""

# Verificar se o sistema já está instalado
if [ -d "/opt/erp-system" ]; then
    warning "Sistema ERP já parece estar instalado em /opt/erp-system"
    read -p "Deseja continuar e reinstalar? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Instalação cancelada"
        exit 0
    fi
fi

# Verificar conectividade com internet
log "🌐 Verificando conectividade..."
if ! ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    error "Sem conectividade com a internet"
fi

# Atualizar sistema
log "📋 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências essenciais
log "📦 Instalando dependências do sistema..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git curl wget net-tools

# Baixar código do GitHub
log "📥 Baixando código do GitHub..."
cd /tmp
rm -rf erp-system-temp
git clone $GITHUB_REPO erp-system-temp

if [ ! -d "erp-system-temp" ]; then
    error "Falha ao baixar código do GitHub"
fi

# Executar script de deploy
log "🔧 Executando deploy..."
cd erp-system-temp
chmod +x scripts/deploy/deploy.sh
./scripts/deploy/deploy.sh $GITHUB_REPO

# Verificar instalação
log "✅ Verificando instalação..."
sleep 5

# Testar aplicação
if curl -s http://localhost/health > /dev/null; then
    log "🎉 Instalação concluída com sucesso!"
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo ""
    echo "=========================================="
    echo "🚀 SISTEMA ERP INSTALADO COM SUCESSO!"
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
else
    warning "⚠️ Aplicação pode não estar respondendo ainda"
    log "Verifique os logs: erp-manage logs"
fi
