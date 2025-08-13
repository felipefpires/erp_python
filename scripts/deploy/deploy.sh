#!/bin/bash

# Script de Deploy Automatizado - Sistema ERP
# Execute este script no servidor Ubuntu
# Uso: ./deploy.sh [GITHUB_REPO_URL]

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
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

# Configurações
APP_NAME="erp-system"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="erp-system"
USER_NAME="erp"
BACKUP_DIR="$APP_DIR/backups"
LOG_DIR="$APP_DIR/logs"

# GitHub repository (pode ser passado como parâmetro)
GITHUB_REPO=${1:-"https://github.com/seu-usuario/erp-project.git"}

log "🚀 Iniciando deploy automatizado do Sistema ERP..."
log "📦 Repositório: $GITHUB_REPO"

# Função para fazer backup
backup_existing() {
    if [ -d "$APP_DIR" ] && [ -f "$APP_DIR/instance/erp.db" ]; then
        log "💾 Fazendo backup do sistema existente..."
        sudo mkdir -p "$BACKUP_DIR"
        BACKUP_FILE="erp_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
        sudo tar -czf "$BACKUP_DIR/$BACKUP_FILE" -C "$APP_DIR" instance/ uploads/ .env 2>/dev/null || true
        log "✅ Backup criado: $BACKUP_FILE"
    fi
}

# Função para restaurar backup
restore_backup() {
    if [ -d "$BACKUP_DIR" ] && [ "$(ls -A $BACKUP_DIR)" ]; then
        log "🔄 Restaurando backup..."
        LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/erp_backup_*.tar.gz 2>/dev/null | head -1)
        if [ -n "$LATEST_BACKUP" ]; then
            sudo tar -xzf "$LATEST_BACKUP" -C "$APP_DIR"
            log "✅ Backup restaurado: $(basename $LATEST_BACKUP)"
        fi
    fi
}

# Função para limpar backups antigos
cleanup_backups() {
    if [ -d "$BACKUP_DIR" ]; then
        log "🧹 Limpando backups antigos..."
        sudo find "$BACKUP_DIR" -name "erp_backup_*.tar.gz" -type f -mtime +7 -delete 2>/dev/null || true
    fi
}

# Verificar e instalar dependências do sistema
log "📋 Verificando dependências do sistema..."

# Atualizar sistema
sudo apt update

# Instalar dependências essenciais
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git curl wget net-tools

# Criar usuário para a aplicação
if ! id "$USER_NAME" &>/dev/null; then
    log "👤 Criando usuário $USER_NAME..."
    sudo useradd -r -s /bin/bash -d $APP_DIR $USER_NAME
    sudo usermod -aG sudo $USER_NAME
else
    log "👤 Usuário $USER_NAME já existe"
fi

# Fazer backup antes de prosseguir
backup_existing

# Criar diretório da aplicação
log "📁 Preparando diretório da aplicação..."
sudo mkdir -p $APP_DIR
sudo chown $USER_NAME:$USER_NAME $APP_DIR

# Clonar código do GitHub
log "📦 Clonando código do GitHub..."
cd /tmp
sudo rm -rf erp-system-temp
sudo -u $USER_NAME git clone $GITHUB_REPO erp-system-temp

# Copiar código para diretório final
log "📁 Copiando código para diretório final..."
sudo cp -r erp-system-temp/* $APP_DIR/
sudo chown -R $USER_NAME:$USER_NAME $APP_DIR

# Criar ambiente virtual
log "🐍 Criando ambiente virtual Python..."
sudo -u $USER_NAME python3 -m venv $VENV_DIR

# Ativar ambiente virtual e instalar dependências
log "📦 Instalando dependências Python..."
sudo -u $USER_NAME $VENV_DIR/bin/pip install --upgrade pip
sudo -u $USER_NAME $VENV_DIR/bin/pip install gunicorn
sudo -u $USER_NAME $VENV_DIR/bin/pip install -r $APP_DIR/requirements.txt

# Criar diretórios necessários
log "📁 Criando diretórios da aplicação..."
sudo -u $USER_NAME mkdir -p $APP_DIR/instance
sudo -u $USER_NAME mkdir -p $APP_DIR/uploads
sudo -u $USER_NAME mkdir -p $LOG_DIR
sudo -u $USER_NAME mkdir -p $BACKUP_DIR

# Configurar variáveis de ambiente
log "⚙️ Configurando variáveis de ambiente..."
sudo -u $USER_NAME tee $APP_DIR/.env > /dev/null <<EOF
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///$APP_DIR/instance/erp.db
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=False
HOST=0.0.0.0
PORT=5000
EOF

# Restaurar backup se existir
restore_backup

# Configurar Supervisor
log "🔧 Configurando Supervisor..."
sudo tee /etc/supervisor/conf.d/$SERVICE_NAME.conf > /dev/null <<EOF
[program:$SERVICE_NAME]
command=$VENV_DIR/bin/gunicorn --workers 3 --bind unix:$APP_DIR/$SERVICE_NAME.sock --access-logfile $LOG_DIR/access.log --error-logfile $LOG_DIR/error.log --log-level info wsgi:app
directory=$APP_DIR
user=$USER_NAME
autostart=true
autorestart=true
startretries=3
startsecs=5
stderr_logfile=$LOG_DIR/supervisor_err.log
stdout_logfile=$LOG_DIR/supervisor_out.log
environment=FLASK_ENV="production"
EOF

# Configurar Nginx corretamente
log "🌐 Configurando Nginx..."

# Limpar configurações existentes
sudo rm -f /etc/nginx/sites-enabled/*
sudo rm -f /etc/nginx/sites-available/$SERVICE_NAME

# Criar configuração limpa
sudo tee /etc/nginx/sites-available/$SERVICE_NAME > /dev/null <<EOF
server {
    listen 80 default_server;
    server_name _;

    # Logs
    access_log /var/log/nginx/erp_access.log;
    error_log /var/log/nginx/erp_error.log;

    # Proxy para aplicação
    location / {
        proxy_pass http://unix:$APP_DIR/$SERVICE_NAME.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Arquivos estáticos
    location /static {
        alias $APP_DIR/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Uploads
    location /uploads {
        alias $APP_DIR/uploads;
        expires 30d;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "OK";
        add_header Content-Type text/plain;
    }
}
EOF

# Ativar apenas nosso site
sudo ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/

# Verificar configuração do Nginx
log "🔍 Verificando configuração do Nginx..."
sudo nginx -t

# Inicializar banco de dados
log "🗄️ Inicializando banco de dados..."
cd $APP_DIR
sudo -u $USER_NAME $VENV_DIR/bin/python init_db.py

# Configurar permissões
log "🔐 Configurando permissões..."
sudo chown -R $USER_NAME:$USER_NAME $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod 664 $APP_DIR/instance/erp.db

# Reiniciar serviços
log "🔄 Reiniciando serviços..."
sudo systemctl reload nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start $SERVICE_NAME

# Aguardar um pouco para os serviços iniciarem
sleep 5

# Verificar se os serviços estão rodando
log "✅ Verificando status dos serviços..."

# Verificar Supervisor
if sudo supervisorctl status $SERVICE_NAME | grep -q "RUNNING"; then
    log "✅ Supervisor: $SERVICE_NAME está RUNNING"
else
    error "❌ Supervisor: $SERVICE_NAME não está rodando"
fi

# Verificar Nginx
if sudo systemctl is-active --quiet nginx; then
    log "✅ Nginx está ativo"
else
    error "❌ Nginx não está ativo"
fi

# Verificar socket
if [ -S "$APP_DIR/$SERVICE_NAME.sock" ]; then
    log "✅ Socket Unix criado: $APP_DIR/$SERVICE_NAME.sock"
else
    error "❌ Socket Unix não foi criado"
fi

# Testar aplicação
log "🧪 Testando aplicação..."
sleep 2
if curl -s http://localhost/health > /dev/null; then
    log "✅ Aplicação respondendo corretamente"
else
    warning "⚠️ Aplicação pode não estar respondendo ainda"
fi

# Limpar backups antigos
cleanup_backups

# Mostrar informações finais
SERVER_IP=$(hostname -I | awk '{print $1}')
log "🎉 Deploy concluído com sucesso!"
log "🌐 Acesse: http://$SERVER_IP"
log "📁 Logs: $LOG_DIR/"
log "🔧 Para gerenciar: erp-manage status"
log "💾 Backups: $BACKUP_DIR/"

# Instalar script de gerenciamento
if [ -f "$APP_DIR/scripts/deploy/manage.sh" ]; then
    sudo cp $APP_DIR/scripts/deploy/manage.sh /usr/local/bin/erp-manage
    sudo chmod +x /usr/local/bin/erp-manage
    log "✅ Script de gerenciamento instalado: erp-manage"
fi

log "🚀 Sistema ERP pronto para uso!"
