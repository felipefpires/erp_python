#!/usr/bin/env python3
"""
Script para inicializar o banco de dados e criar usuário administrador
"""

from app import create_app, db
from app.models.user import User
from app.models.inventory import Category
from app.models.finance import Account

def init_database():
    app = create_app()
    
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Verificar se já existe um usuário administrador
        admin = User.query.filter_by(username='admin').first()
        if not admin:
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
        else:
            print("✅ Banco de dados já inicializado!")
            print("👤 Usuário administrador já existe")

if __name__ == '__main__':
    init_database()


