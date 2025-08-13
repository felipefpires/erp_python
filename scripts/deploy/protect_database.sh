#!/bin/bash

# Script para proteger o banco de dados em produção
# Este script garante que o banco de dados não seja modificado após a inicialização

set -e

echo "🔒 Protegendo Banco de Dados em Produção"
echo "========================================"

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root (use sudo)"
    exit 1
fi

APP_DIR="/opt/erp-system"
DB_FILE="$APP_DIR/instance/erp.db"
BACKUP_DIR="/opt/backups/erp"

# Verificar se o banco de dados existe
if [ ! -f "$DB_FILE" ]; then
    echo "❌ Banco de dados não encontrado: $DB_FILE"
    exit 1
fi

echo "📊 Banco de dados encontrado: $DB_FILE"

# Fazer backup antes de proteger
echo "💾 Criando backup antes da proteção..."
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/erp_protected_$DATE.db"
mkdir -p $BACKUP_DIR
cp "$DB_FILE" "$BACKUP_FILE"
echo "✅ Backup criado: $BACKUP_FILE"

# Configurar permissões restritivas
echo "🔐 Configurando permissões restritivas..."
chown erp:erp "$DB_FILE"
chmod 640 "$DB_FILE"

# Tornar o arquivo somente leitura
echo "📝 Tornando banco de dados somente leitura..."
chmod 440 "$DB_FILE"

# Criar script para desproteger temporariamente (apenas para manutenção)
echo "🔧 Criando script de manutenção..."
cat > /usr/local/bin/erp-db-maintenance << 'EOF'
#!/bin/bash

# Script para manutenção do banco de dados
# Uso: erp-db-maintenance [enable|disable]

DB_FILE="/opt/erp-system/instance/erp.db"

if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root (use sudo)"
    exit 1
fi

case "$1" in
    enable)
        echo "🔓 Habilitando escrita no banco de dados..."
        chmod 640 "$DB_FILE"
        echo "✅ Banco de dados habilitado para escrita"
        echo "⚠️ Lembre-se de executar 'erp-db-maintenance disable' após a manutenção"
        ;;
    disable)
        echo "🔒 Desabilitando escrita no banco de dados..."
        chmod 440 "$DB_FILE"
        echo "✅ Banco de dados protegido contra escrita"
        ;;
    *)
        echo "Uso: $0 [enable|disable]"
        echo "  enable  - Habilitar escrita no banco de dados"
        echo "  disable - Desabilitar escrita no banco de dados"
        exit 1
        ;;
esac
EOF

chmod +x /usr/local/bin/erp-db-maintenance

# Modificar o script init_db.py para verificar se está em produção
echo "🔧 Modificando script de inicialização..."
if [ -f "$APP_DIR/init_db.py" ]; then
    # Fazer backup do script original
    cp "$APP_DIR/init_db.py" "$APP_DIR/init_db.py.backup"
    
    # Adicionar verificação de produção
    cat > "$APP_DIR/init_db_production.py" << 'EOF'
#!/usr/bin/env python3
"""
Script para inicializar o banco de dados em produção
Este script só deve ser executado uma vez após a instalação
"""

import os
import sys
from app import create_app, db
from app.models.user import User
from app.models.inventory import Category
from app.models.finance import Account

def init_database():
    # Verificar se está em produção
    if os.environ.get('FLASK_ENV') != 'production':
        print("❌ Este script deve ser executado apenas em produção")
        sys.exit(1)
    
    app = create_app()
    
    with app.app_context():
        # Verificar se o banco já foi inicializado
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("✅ Banco de dados já inicializado!")
            print("👤 Usuário administrador já existe")
            print("🔒 Banco de dados está protegido contra modificações")
            return
        
        # Criar todas as tabelas
        db.create_all()
        
        # Criar usuário administrador
        admin = User(
            username='admin',
            email='admin@erp.com',
            first_name='Administrador',
            last_name='Sistema',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Criar categorias padrão
        categories = [
            Category(name='Eletrônicos', description='Produtos eletrônicos'),
            Category(name='Vestuário', description='Roupas e acessórios'),
            Category(name='Casa', description='Produtos para casa'),
            Category(name='Livros', description='Livros e publicações'),
            Category(name='Outros', description='Outros produtos')
        ]
        
        for category in categories:
            db.session.add(category)
        
        # Criar conta padrão
        default_account = Account(
            name='Caixa Principal',
            account_type='caixa',
            initial_balance=0,
            current_balance=0
        )
        db.session.add(default_account)
        
        db.session.commit()
        print("✅ Banco de dados inicializado com sucesso!")
        print("👤 Usuário administrador criado:")
        print("   Usuário: admin")
        print("   Senha: admin123")
        print("   Email: admin@erp.com")
        print("🔒 Banco de dados será protegido contra modificações")

if __name__ == '__main__':
    init_database()
EOF

    chown erp:erp "$APP_DIR/init_db_production.py"
    chmod +x "$APP_DIR/init_db_production.py"
fi

# Modificar o workflow do GitHub Actions para não executar init_db.py
echo "🔧 Atualizando workflow do GitHub Actions..."
if [ -f "$APP_DIR/.github/workflows/deploy.yml" ]; then
    # Fazer backup do workflow original
    cp "$APP_DIR/.github/workflows/deploy.yml" "$APP_DIR/.github/workflows/deploy.yml.backup"
    
    # Substituir a linha que executa init_db.py
    sed -i 's/python init_db.py/# python init_db.py  # Desabilitado em produção/' "$APP_DIR/.github/workflows/deploy.yml"
fi

echo ""
echo "✅ Proteção do banco de dados concluída!"
echo ""
echo "📋 Informações importantes:"
echo "🔒 O banco de dados agora está protegido contra modificações"
echo "🔧 Para manutenção, use: erp-db-maintenance enable"
echo "🔒 Após manutenção, use: erp-db-maintenance disable"
echo "💾 Backup criado: $BACKUP_FILE"
echo ""
echo "⚠️ ATENÇÃO:"
echo "- O script init_db.py foi desabilitado no workflow do GitHub Actions"
echo "- Use init_db_production.py apenas uma vez após a instalação"
echo "- O banco de dados não será mais modificado automaticamente"
