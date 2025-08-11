#!/bin/bash

# Script de Deploy Manual - Sistema ERP
# Copie e cole este script no console da VM Ubuntu

echo "🚀 Iniciando deploy manual do Sistema ERP..."

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERRO] $1${NC}"
    exit 1
}

# Verificar se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    error "Execute este script no diretório do projeto (onde está requirements.txt)"
fi

log "📋 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

log "📦 Instalando dependências do sistema..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git curl wget

log "👤 Criando usuário erp..."
sudo useradd -r -s /bin/bash -d /opt/erp-system erp

log "📁 Criando diretório da aplicação..."
sudo mkdir -p /opt/erp-system
sudo chown erp:erp /opt/erp-system

log "📦 Copiando código..."
sudo cp -r . /opt/erp-system/
sudo chown -R erp:erp /opt/erp-system

log "🐍 Criando ambiente virtual..."
sudo -u erp python3 -m venv /opt/erp-system/venv

log "📦 Instalando dependências Python..."
sudo -u erp /opt/erp-system/venv/bin/pip install --upgrade pip
sudo -u erp /opt/erp-system/venv/bin/pip install -r /opt/erp-system/requirements.txt

log "📁 Criando diretórios necessários..."
sudo -u erp mkdir -p /opt/erp-system/instance
sudo -u erp mkdir -p /opt/erp-system/uploads
sudo -u erp mkdir -p /opt/erp-system/logs
sudo -u erp mkdir -p /opt/erp-system/backups

log "⚙️ Configurando variáveis de ambiente..."
sudo -u erp tee /opt/erp-system/.env > /dev/null <<EOF
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:////opt/erp-system/instance/erp.db
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=False
EOF

log "🔧 Configurando Supervisor..."
sudo tee /etc/supervisor/conf.d/erp-system.conf > /dev/null <<EOF
[program:erp-system]
command=/opt/erp-system/venv/bin/gunicorn --workers 3 --bind unix:/opt/erp-system/erp-system.sock --access-logfile /opt/erp-system/logs/access.log --error-logfile /opt/erp-system/logs/error.log wsgi:app
directory=/opt/erp-system
user=erp
autostart=true
autorestart=true
stderr_logfile=/opt/erp-system/logs/supervisor_err.log
stdout_logfile=/opt/erp-system/logs/supervisor_out.log
EOF

log "🌐 Configurando Nginx..."
sudo tee /etc/nginx/sites-available/erp-system > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/erp-system/erp-system.sock;
    }

    location /static {
        alias /opt/erp-system/app/static;
    }

    location /uploads {
        alias /opt/erp-system/uploads;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/erp-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

log "🗄️ Inicializando banco de dados..."
cd /opt/erp-system
sudo -u erp /opt/erp-system/venv/bin/python init_db.py

log "🔄 Iniciando serviços..."
sudo systemctl restart supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start erp-system
sudo systemctl restart nginx

log "✅ Verificando status..."
sudo supervisorctl status erp-system
sudo systemctl status nginx --no-pager -l

log "🎉 Deploy concluído!"
log "🌐 Acesse: http://$(hostname -I | awk '{print $1}')"
log "📁 Logs: /opt/erp-system/logs/"
log "🔧 Para gerenciar: sudo supervisorctl status erp-system"

# Criar script de gerenciamento
log "🔧 Criando script de gerenciamento..."
sudo tee /usr/local/bin/erp-manage > /dev/null <<'EOF'
#!/bin/bash

APP_DIR="/opt/erp-system"
SERVICE_NAME="erp-system"

case "$1" in
    start)
        sudo supervisorctl start $SERVICE_NAME
        sudo systemctl start nginx
        echo "Sistema iniciado!"
        ;;
    stop)
        sudo supervisorctl stop $SERVICE_NAME
        sudo systemctl stop nginx
        echo "Sistema parado!"
        ;;
    restart)
        sudo supervisorctl restart $SERVICE_NAME
        sudo systemctl reload nginx
        echo "Sistema reiniciado!"
        ;;
    status)
        echo "=== Supervisor ==="
        sudo supervisorctl status $SERVICE_NAME
        echo "=== Nginx ==="
        sudo systemctl status nginx --no-pager -l
        ;;
    logs)
        echo "=== Logs de Erro ==="
        tail -20 $APP_DIR/logs/error.log
        echo "=== Logs de Acesso ==="
        tail -20 $APP_DIR/logs/access.log
        ;;
    backup)
        BACKUP_FILE="erp_backup_$(date +%Y%m%d_%H%M%S).db"
        sudo -u erp cp $APP_DIR/instance/erp.db $APP_DIR/backups/$BACKUP_FILE
        echo "Backup criado: $BACKUP_FILE"
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs|backup}"
        exit 1
        ;;
esac
EOF

sudo chmod +x /usr/local/bin/erp-manage

log "✅ Script de gerenciamento criado!"
log "📋 Comandos disponíveis:"
echo "   erp-manage status    # Ver status"
echo "   erp-manage logs      # Ver logs"
echo "   erp-manage restart   # Reiniciar"
echo "   erp-manage backup    # Fazer backup"

