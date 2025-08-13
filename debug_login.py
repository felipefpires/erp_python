#!/usr/bin/env python3
"""
Script para debug do sistema de login
"""

from app import create_app, db
from app.models.user import User

def debug_login():
    app = create_app()
    
    with app.app_context():
        print("🔍 Debug do Sistema de Login")
        print("=" * 40)
        
        # Verificar se o banco existe
        try:
            db.create_all()
            print("✅ Banco de dados criado/verificado")
        except Exception as e:
            print(f"❌ Erro ao criar banco: {e}")
            return
        
        # Verificar usuários existentes
        users = User.query.all()
        print(f"📊 Usuários encontrados: {len(users)}")
        
        for user in users:
            print(f"  👤 {user.username} ({user.email}) - Role: {user.role}")
            print(f"     Ativo: {user.is_active}")
            print(f"     Senha hash: {user.password_hash[:20]}...")
        
        # Testar usuário admin
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"\n🔑 Testando usuário admin:")
            print(f"   Usuário: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Role: {admin.role}")
            print(f"   Ativo: {admin.is_active}")
            
            # Testar senha
            test_password = 'admin123'
            if admin.check_password(test_password):
                print(f"   ✅ Senha '{test_password}' está correta")
            else:
                print(f"   ❌ Senha '{test_password}' está incorreta")
                
            # Verificar se tem password_hash
            if admin.password_hash:
                print(f"   ✅ Tem password_hash configurado")
            else:
                print(f"   ❌ NÃO tem password_hash configurado")
        else:
            print("\n❌ Usuário admin não encontrado!")
            print("   Execute: python init_db.py")
        
        # Verificar configurações da aplicação
        print(f"\n⚙️ Configurações da Aplicação:")
        print(f"   SECRET_KEY: {app.config.get('SECRET_KEY', 'NÃO CONFIGURADO')[:20]}...")
        print(f"   DEBUG: {app.config.get('DEBUG', False)}")
        print(f"   SESSION_COOKIE_SECURE: {app.config.get('SESSION_COOKIE_SECURE', False)}")
        print(f"   SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY', True)}")

if __name__ == '__main__':
    debug_login()
