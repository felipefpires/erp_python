#!/bin/bash

# Script para configurar servidor de produção
# Execute este script como root no servidor Ubuntu

set -e

echo "🚀 Configurando servidor de produção para ERP System..."

# Atualizar sistema
echo "📦 Atualizando sistema..."
apt update && apt upgrade -y

# Instalar dependências
echo "🔧 Instalando dependências..."
apt install -y python3 python3-pip python3-venv git nginx supervisor

# Criar usuário para o serviço
echo "👤 Criando usuário erp..."
useradd -m -s /bin/bash erp || echo "Usuário erp já existe"

# Criar diretório da aplicação
echo "📁 Criando diretório da aplicação..."
mkdir -p /opt/erp-system
chown erp:erp /opt/erp-system

# Perguntar URL do repositório
echo ""
echo "📋 Configuração do Repositório:"
read -p "Digite a URL do seu repositório GitHub: " REPO_URL
read -p "Digite o branch principal (main/master): " BRANCH

# Clonar repositório
echo "📥 Clonando repositório..."
cd /opt
if [ ! -d "erp-system" ]; then
    git clone $REPO_URL erp-system
fi
chown -R erp:erp /opt/erp-system

# Configurar ambiente virtual
echo "🐍 Configurando ambiente virtual..."
cd /opt/erp-system
sudo -u erp python3 -m venv venv
sudo -u erp ./venv/bin/pip install --upgrade pip
sudo -u erp ./venv/bin/pip install -r requirements.txt

# Criar arquivo de configuração
echo "⚙️ Criando arquivo de configuração..."
cat > /opt/erp-system/.env << EOF
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:////opt/erp-system/instance/erp.db
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
EOF

chown erp:erp /opt/erp-system/.env

# Inicializar banco de dados
echo "🗄️ Inicializando banco de dados..."
cd /opt/erp-system
sudo -u erp ./venv/bin/python init_db.py

# Configurar systemd service
echo "🔧 Configurando serviço systemd..."
cat > /etc/systemd/system/erp-system.service << EOF
[Unit]
Description=ERP System
After=network.target

[Service]
Type=simple
User=erp
Group=erp
WorkingDirectory=/opt/erp-system
Environment=PATH=/opt/erp-system/venv/bin
ExecStart=/opt/erp-system/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
echo "🌐 Configurando Nginx..."
cat > /etc/nginx/sites-available/erp-system << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /opt/erp-system/static;
    }
}
EOF

# Ativar site
ln -sf /etc/nginx/sites-available/erp-system /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Configurar firewall
echo "🔥 Configurando firewall..."
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Iniciar serviços
echo "🚀 Iniciando serviços..."
systemctl daemon-reload
systemctl enable erp-system
systemctl start erp-system
systemctl restart nginx

# Configurar backup automático
echo "💾 Configurando backup automático..."
cat > /etc/cron.daily/erp-backup << EOF
#!/bin/bash
BACKUP_DIR="/opt/backups/erp"
DATE=\$(date +%Y%m%d_%H%M%S)
mkdir -p \$BACKUP_DIR
cp /opt/erp-system/instance/erp.db \$BACKUP_DIR/erp_\$DATE.db
find \$BACKUP_DIR -name "*.db" -mtime +7 -delete
EOF

chmod +x /etc/cron.daily/erp-backup

# Configurar script de gerenciamento
echo "🔧 Configurando script de gerenciamento..."
cp /opt/erp-system/scripts/deploy/manage.sh /usr/local/bin/erp-manage
chmod +x /usr/local/bin/erp-manage

echo "✅ Configuração do servidor concluída!"
echo "🌐 Acesse: http://$(hostname -I | awk '{print $1}')"
echo "👤 Usuário admin: admin"
echo "🔑 Senha: admin123"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure os secrets no GitHub:"
echo "   - SERVER_HOST: $(hostname -I | awk '{print $1}')"
echo "   - SERVER_USER: erp"
echo "   - SERVER_SSH_KEY: Sua chave SSH pública"
echo "   - SERVER_PORT: 22"
echo ""
echo "2. Para configurar SSH key:"
echo "   ssh-keygen -t rsa -b 4096 -C 'seu-email@exemplo.com'"
echo "   cat ~/.ssh/id_rsa.pub"
echo ""
echo "3. Adicione a chave pública ao servidor:"
echo "   ssh-copy-id erp@$(hostname -I | awk '{print $1}')"
echo ""
echo "4. Teste o deploy fazendo push para o branch $BRANCH"
echo ""
echo "🔧 Comandos úteis:"
echo "   erp-manage status    - Ver status do sistema"
echo "   erp-manage logs      - Ver logs"
echo "   erp-manage health    - Verificar saúde"
echo "   erp-manage backup    - Fazer backup manual"
