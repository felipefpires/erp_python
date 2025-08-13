#!/bin/bash

# Script de Atualização Automática - Sistema ERP
# Este script pode ser executado via cron para atualizações automáticas
# Uso: ./auto-update.sh [GITHUB_REPO_URL]

set -e

# Configurações
APP_NAME="erp-system"
APP_DIR="/opt/$APP_NAME"
LOG_FILE="/opt/erp-system/logs/auto-update.log"
LOCK_FILE="/tmp/erp-auto-update.lock"

# GitHub repository (pode ser passado como parâmetro)
GITHUB_REPO=${1:-"https://github.com/seu-usuario/erp-project.git"}

# Função para log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Verificar se já está rodando
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat $LOCK_FILE 2>/dev/null)
    if ps -p $PID > /dev/null 2>&1; then
        log "Atualização automática já está rodando (PID: $PID)"
        exit 0
    else
        rm -f $LOCK_FILE
    fi
fi

# Criar arquivo de lock
echo $$ > $LOCK_FILE

# Função para limpar lock
cleanup() {
    rm -f $LOCK_FILE
    exit 0
}

# Capturar sinais para limpeza
trap cleanup SIGINT SIGTERM

log "🔄 Iniciando atualização automática..."

# Verificar se o sistema está instalado
if [ ! -d "$APP_DIR" ]; then
    log "❌ Sistema ERP não encontrado em $APP_DIR"
    cleanup
fi

# Verificar se é um repositório git
if [ ! -d "$APP_DIR/.git" ]; then
    log "❌ Diretório não é um repositório git"
    cleanup
fi

# Verificar conectividade
if ! ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    log "❌ Sem conectividade com a internet"
    cleanup
fi

# Verificar se há atualizações disponíveis
cd $APP_DIR
git fetch origin > /dev/null 2>&1

LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    log "✅ Sistema já está atualizado"
    cleanup
fi

log "📦 Atualizações disponíveis, iniciando atualização..."

# Fazer backup antes da atualização
log "💾 Fazendo backup..."
/usr/local/bin/erp-manage backup

# Parar serviços
log "🛑 Parando serviços..."
/usr/local/bin/erp-manage stop

# Atualizar código
log "📥 Atualizando código..."
git fetch origin
git reset --hard origin/main

# Atualizar dependências
log "📦 Atualizando dependências..."
sudo -u erp /opt/erp-system/venv/bin/pip install -r requirements.txt

# Executar migrações
log "🗄️ Executando migrações..."
sudo -u erp /opt/erp-system/venv/bin/python init_db.py

# Configurar permissões
sudo chown -R erp:erp $APP_DIR

# Reiniciar serviços
log "🚀 Reiniciando serviços..."
/usr/local/bin/erp-manage start

# Aguardar inicialização
sleep 10

# Verificar se está funcionando
if curl -s http://localhost/health > /dev/null; then
    log "✅ Atualização concluída com sucesso!"
else
    log "❌ Erro na atualização - aplicação não está respondendo"
    # Tentar restaurar backup
    log "🔄 Tentando restaurar backup..."
    /usr/local/bin/erp-manage stop
    # Aqui você pode adicionar lógica para restaurar o backup
    /usr/local/bin/erp-manage start
fi

# Limpar logs antigos
log "🧹 Limpando logs antigos..."
/usr/local/bin/erp-manage clean

log "🏁 Atualização automática concluída"

cleanup
