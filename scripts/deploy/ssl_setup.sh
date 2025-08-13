#!/bin/bash

# Script para configurar SSL/HTTPS automaticamente com Let's Encrypt
# Execute este script após a instalação inicial

set -e

echo "🔒 Configurando SSL/HTTPS com Let's Encrypt"
echo "=========================================="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root (use sudo)"
    exit 1
fi

# Perguntar domínio
read -p "Digite seu domínio (ex: erp.seudominio.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo "❌ Domínio é obrigatório"
    exit 1
fi

# Instalar Certbot
echo "📦 Instalando Certbot..."
apt update
apt install -y certbot python3-certbot-nginx

# Configurar Nginx para o domínio
echo "🌐 Configurando Nginx para $DOMAIN..."
cat > /etc/nginx/sites-available/erp-system << EOF
server {
    listen 80;
    server_name $DOMAIN;

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

# Testar configuração do Nginx
nginx -t

# Reiniciar Nginx
systemctl restart nginx

# Obter certificado SSL
echo "🔒 Obtendo certificado SSL..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Configurar renovação automática
echo "🔄 Configurando renovação automática..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Configurar redirecionamento HTTP para HTTPS
echo "🔄 Configurando redirecionamento HTTP para HTTPS..."
cat > /etc/nginx/sites-available/erp-system << EOF
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

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

# Testar e reiniciar Nginx
nginx -t
systemctl restart nginx

echo "✅ SSL/HTTPS configurado com sucesso!"
echo "🌐 Acesse: https://$DOMAIN"
echo "🔒 Certificado será renovado automaticamente"
echo ""
echo "📋 Informações importantes:"
echo "- Certificado válido por 90 dias"
echo "- Renovação automática configurada"
echo "- Redirecionamento HTTP → HTTPS ativo"
