#!/bin/bash

# Script para instalação limpa em servidor novo
# Este script remove qualquer instalação anterior e instala do zero

set -e

echo "🧹 Instalação Limpa do Sistema ERP"
echo "=================================="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root (use sudo)"
    exit 1
fi

# Confirmar instalação limpa
echo "⚠️ ATENÇÃO: Este script irá remover qualquer instalação anterior do ERP System!"
read -p "Deseja continuar? (digite 'SIM' para confirmar): " CONFIRM

if [ "$CONFIRM" != "SIM" ]; then
    echo "❌ Instalação cancelada"
    exit 1
fi

echo "🧹 Removendo instalações anteriores..."

# Parar e remover serviços
systemctl stop erp-system 2>/dev/null || true
systemctl disable erp-system 2>/dev/null || true
rm -f /etc/systemd/system/erp-system.service

# Remover configurações do Nginx
rm -f /etc/nginx/sites-enabled/erp-system
rm -f /etc/nginx/sites-available/erp-system

# Remover diretórios
rm -rf /opt/erp-system
rm -rf /opt/backups/erp

# Remover usuário (se existir)
userdel -r erp 2>/dev/null || true

# Limpar logs
journalctl --vacuum-time=1d

echo "✅ Limpeza concluída!"
echo ""
echo "🚀 Iniciando instalação limpa..."

# Executar instalação
chmod +x scripts/deploy/setup_production.sh
./scripts/deploy/setup_production.sh

echo ""
echo "✅ Instalação limpa concluída com sucesso!"
echo "🌐 Acesse: http://$(hostname -I | awk '{print $1}')"
echo "👤 Usuário admin: admin"
echo "�� Senha: admin123"
