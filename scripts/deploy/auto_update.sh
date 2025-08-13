#!/bin/bash

# Script para atualização automática do ERP System
# Este script é executado pelo GitHub Actions

set -e

echo "🔄 Iniciando atualização automática..."

# Navegar para o diretório da aplicação
cd /opt/erp-system

# Fazer backup antes da atualização
echo "💾 Criando backup..."
BACKUP_DIR="/opt/backups/erp"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp instance/erp.db $BACKUP_DIR/erp_backup_$DATE.db

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar dependências
echo "📦 Atualizando dependências..."
pip install -r requirements.txt

# Verificar se há mudanças no banco de dados
echo "🗄️ Verificando estrutura do banco de dados..."
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.create_all()
        print('✅ Estrutura do banco de dados atualizada')
    except Exception as e:
        print(f'⚠️ Aviso: {e}')
"

# Reiniciar serviço
echo "🔄 Reiniciando serviço..."
sudo systemctl restart erp-system

# Verificar status do serviço
echo "🔍 Verificando status do serviço..."
sleep 5
if systemctl is-active --quiet erp-system; then
    echo "✅ Serviço iniciado com sucesso!"
else
    echo "❌ Erro ao iniciar serviço. Restaurando backup..."
    cp $BACKUP_DIR/erp_backup_$DATE.db instance/erp.db
    sudo systemctl restart erp-system
    exit 1
fi

# Limpar backups antigos (manter apenas 7 dias)
echo "🧹 Limpando backups antigos..."
find $BACKUP_DIR -name "*.db" -mtime +7 -delete

echo "✅ Atualização concluída com sucesso!"
