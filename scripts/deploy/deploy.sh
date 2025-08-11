#!/bin/bash

# Script de Deploy - Sistema ERP
# Execute este script no servidor Ubuntu

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do Sistema ERP..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

log "📋 Verificando dependências do sistema..."

# Atualizar sistema
sudo apt update

# Instalar dependências
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git curl

# Criar usuário para a aplicação
if ! id "$USER_NAME" &>/dev/null; then
    log "👤 Criando usuário $USER_NAME..."
    sudo useradd -r -s /bin/bash -d $APP_DIR $USER_NAME
else
    log "👤 Usuário $USER_NAME já existe"
fi

# Criar diretório da aplicação
log "📁 Criando diretório da aplicação..."
sudo mkdir -p $APP_DIR
sudo chown $USER_NAME:$USER_NAME $APP_DIR

# Clonar/copiar código (assumindo que o código já está no servidor)
log "📦 Copiando código da aplicação..."
# Se você já tem o código no servidor, copie para $APP_DIR
# sudo cp -r . $APP_DIR/
# sudo chown -R $USER_NAME:$USER_NAME $APP_DIR

# Criar ambiente virtual
log "🐍 Criando ambiente virtual Python..."
sudo -u $USER_NAME python3 -m venv $VENV_DIR

# Ativar ambiente virtual e instalar dependências
log "📦 Instalando dependências Python..."
sudo -u $USER_NAME $VENV_DIR/bin/pip install --upgrade pip
sudo -u $USER_NAME $VENV_DIR/bin/pip install -r $APP_DIR/requirements.txt

# Criar diretórios necessários
log "📁 Criando diretórios da aplicação..."
sudo -u $USER_NAME mkdir -p $APP_DIR/instance
sudo -u $USER_NAME mkdir -p $APP_DIR/uploads
sudo -u $USER_NAME mkdir -p $APP_DIR/logs

# Configurar variáveis de ambiente
log "⚙️ Configurando variáveis de ambiente..."
sudo -u $USER_NAME tee $APP_DIR/.env > /dev/null <<EOF
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///$APP_DIR/instance/erp.db
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=False
EOF

# Configurar Supervisor
log "🔧 Configurando Supervisor..."
sudo tee /etc/supervisor/conf.d/$SERVICE_NAME.conf > /dev/null <<EOF
[program:$SERVICE_NAME]
command=$VENV_DIR/bin/gunicorn --workers 3 --bind unix:$APP_DIR/$SERVICE_NAME.sock --access-logfile $APP_DIR/logs/access.log --error-logfile $APP_DIR/logs/error.log wsgi:app
directory=$APP_DIR
user=$USER_NAME
autostart=true
autorestart=true
stderr_logfile=$APP_DIR/logs/supervisor_err.log
stdout_logfile=$APP_DIR/logs/supervisor_out.log
EOF

# Configurar Nginx
log "🌐 Configurando Nginx..."
sudo tee /etc/nginx/sites-available/$SERVICE_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name _;  # Substitua pelo seu domínio

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/$SERVICE_NAME.sock;
    }

    location /static {
        alias $APP_DIR/app/static;
    }

    location /uploads {
        alias $APP_DIR/uploads;
    }
}
EOF

# Ativar site no Nginx
sudo ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Inicializar banco de dados
log "🗄️ Inicializando banco de dados..."
cd $APP_DIR
sudo -u $USER_NAME $VENV_DIR/bin/python init_db.py

# Reiniciar serviços
log "🔄 Reiniciando serviços..."
sudo systemctl reload nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start $SERVICE_NAME

# Verificar status
log "✅ Verificando status dos serviços..."
sudo supervisorctl status $SERVICE_NAME
sudo systemctl status nginx --no-pager -l

log "🎉 Deploy concluído com sucesso!"
log "🌐 Acesse: http://$(hostname -I | awk '{print $1}')"
log "📁 Logs: $APP_DIR/logs/"
log "🔧 Para gerenciar: sudo supervisorctl status $SERVICE_NAME"
