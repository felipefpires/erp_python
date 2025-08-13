#!/bin/bash

# Script para corrigir problemas de sessão no servidor
# Execute este script no servidor Ubuntu

set -e

echo "🔧 Corrigindo Problemas de Sessão no Servidor"
echo "============================================="

APP_DIR="/opt/erp-system"
ENV_FILE="$APP_DIR/.env"

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root (use sudo)"
    exit 1
fi

# Verificar se o diretório da aplicação existe
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Diretório da aplicação não encontrado: $APP_DIR"
    exit 1
fi

echo "📁 Diretório da aplicação: $APP_DIR"

# Fazer backup do arquivo .env atual
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup do arquivo .env criado"
fi

# Gerar nova SECRET_KEY
echo "🔑 Gerando nova SECRET_KEY..."
NEW_SECRET_KEY=$(openssl rand -hex 32)
echo "   Nova SECRET_KEY: ${NEW_SECRET_KEY:0:20}..."

# Criar/atualizar arquivo .env
echo "⚙️ Atualizando arquivo .env..."
cat > "$ENV_FILE" << EOF
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=$NEW_SECRET_KEY
DATABASE_URL=sqlite:////opt/erp-system/instance/erp.db
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
EOF

# Configurar permissões
chown erp:erp "$ENV_FILE"
chmod 600 "$ENV_FILE"

echo "✅ Arquivo .env atualizado com permissões corretas"

# Verificar configurações do Nginx
echo "🌐 Verificando configuração do Nginx..."
NGINX_CONFIG="/etc/nginx/sites-available/erp-system"

if [ -f "$NGINX_CONFIG" ]; then
    echo "✅ Configuração do Nginx encontrada"
    
    # Verificar se há configurações de proxy para sessões
    if grep -q "proxy_set_header.*Host" "$NGINX_CONFIG"; then
        echo "✅ Headers de proxy configurados"
    else
        echo "⚠️ Headers de proxy podem estar incompletos"
    fi
else
    echo "❌ Configuração do Nginx não encontrada"
fi

# Reiniciar serviços
echo "🔄 Reiniciando serviços..."
systemctl restart erp-system
systemctl restart nginx

# Verificar status dos serviços
echo "📊 Verificando status dos serviços..."
sleep 3

if systemctl is-active --quiet erp-system; then
    echo "✅ Serviço ERP ativo"
else
    echo "❌ Serviço ERP inativo"
    echo "   Verifique os logs: journalctl -u erp-system -n 50"
fi

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx ativo"
else
    echo "❌ Nginx inativo"
    echo "   Verifique os logs: journalctl -u nginx -n 50"
fi

# Testar conectividade
echo "🧪 Testando conectividade..."
if curl -s http://localhost/ > /dev/null; then
    echo "✅ Aplicação respondendo localmente"
else
    echo "❌ Aplicação não responde localmente"
fi

echo ""
echo "✅ Correção de sessão concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Teste o login novamente no navegador"
echo "2. Se ainda houver problemas, verifique os logs:"
echo "   journalctl -u erp-system -f"
echo "3. Para verificar cookies:"
echo "   curl -c cookies.txt -b cookies.txt http://localhost/login"
echo ""
echo "🔧 Comandos úteis:"
echo "   erp-manage status    - Ver status do sistema"
echo "   erp-manage logs      - Ver logs"
echo "   erp-manage restart   - Reiniciar sistema"
