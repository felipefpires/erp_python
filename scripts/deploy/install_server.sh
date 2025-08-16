#!/bin/bash

# Script de instalação para servidor Ubuntu
# Execute este script diretamente no servidor Ubuntu como root

set -e

echo "🚀 Instalador do Sistema ERP para Servidor Ubuntu"
echo "=================================================="

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

if [ -z "$REPO_URL" ] || [ -z "$BRANCH" ]; then
    echo "❌ URL do repositório e branch são obrigatórios"
    exit 1
fi

# Baixar o projeto
echo ""
echo "📥 Baixando projeto do GitHub..."
mkdir -p /opt/erp-system
cd /opt/erp-system
git clone $REPO_URL .
chown -R erp:erp /opt/erp-system

# Verificar se o diretório scripts/deploy existe
if [ ! -d "scripts/deploy" ]; then
    echo "❌ Diretório scripts/deploy não encontrado no repositório"
    exit 1
fi

# Executar script de configuração
echo ""
echo "🔧 Executando configuração automática..."
chmod +x scripts/deploy/setup_production.sh

# Substituir URL do repositório no script
sed -i "s|REPO_URL=.*|REPO_URL=\"$REPO_URL\"|g" scripts/deploy/setup_production.sh
sed -i "s|BRANCH=.*|BRANCH=\"$BRANCH\"|g" scripts/deploy/setup_production.sh

# Executar configuração
./scripts/deploy/setup_production.sh

# Limpar arquivos temporários

echo ""
echo "✅ Instalação concluída com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure os secrets no GitHub:"
echo "   - SERVER_HOST: $(hostname -I | awk '{print $1}')"
echo "   - SERVER_USER: erp"
echo "   - SERVER_SSH_KEY: Conteúdo da chave privada SSH"
echo "   - SERVER_PORT: 22"
echo ""
echo "2. Para gerar chave SSH:"
echo "   ssh-keygen -t rsa -b 4096 -C 'seu-email@exemplo.com'"
echo "   cat ~/.ssh/id_rsa"
echo ""
echo "3. Teste o deploy fazendo push para o branch $BRANCH"
echo ""
echo "🔧 Comandos úteis:"
echo "   erp-manage status    - Ver status do sistema"
echo "   erp-manage logs      - Ver logs"
echo "   erp-manage health    - Verificar saúde"
echo "   erp-manage backup    - Fazer backup manual"
