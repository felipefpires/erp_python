#!/bin/bash

# Script de instalação para servidor de produção
# Execute este script no servidor para configurar tudo automaticamente

set -e

echo "🚀 Instalador Automático do ERP System"
echo "======================================"

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root (use sudo)"
    exit 1
fi

# Verificar se é Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo "❌ Este script é compatível apenas com sistemas Ubuntu/Debian"
    exit 1
fi

# Perguntar informações do repositório
echo ""
echo "📋 Configuração do Repositório:"
read -p "Digite a URL do seu repositório GitHub: " REPO_URL
read -p "Digite o branch principal (main/master): " BRANCH

# Executar script de configuração
echo ""
echo "🔧 Executando configuração automática..."
chmod +x scripts/deploy/setup_production.sh

# Substituir URL do repositório no script
sed -i "s|https://github.com/SEU_USUARIO/erp-project.git|$REPO_URL|g" scripts/deploy/setup_production.sh

# Executar configuração
./scripts/deploy/setup_production.sh

echo ""
echo "✅ Instalação concluída!"
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
