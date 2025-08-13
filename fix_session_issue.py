#!/usr/bin/env python3
"""
Script para corrigir problemas de sessão no servidor
"""

from app import create_app, db
from app.models.user import User

def fix_session_issues():
    app = create_app()
    
    with app.app_context():
        print("🔧 Corrigindo Problemas de Sessão")
        print("=" * 40)
        
        # Verificar configurações atuais
        print("📋 Configurações atuais:")
        print(f"   SECRET_KEY: {app.config.get('SECRET_KEY', 'NÃO CONFIGURADO')[:20]}...")
        print(f"   SESSION_COOKIE_SECURE: {app.config.get('SESSION_COOKIE_SECURE', False)}")
        print(f"   SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY', True)}")
        print(f"   SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE', 'Lax')}")
        print(f"   SESSION_COOKIE_DOMAIN: {app.config.get('SESSION_COOKIE_DOMAIN', None)}")
        print(f"   SESSION_COOKIE_PATH: {app.config.get('SESSION_COOKIE_PATH', '/')}")
        
        # Verificar se o SECRET_KEY está configurado corretamente
        if not app.config.get('SECRET_KEY') or app.config.get('SECRET_KEY') == 'dev-secret-key-change-in-production':
            print("\n⚠️ SECRET_KEY não está configurado corretamente!")
            print("   Isso pode causar problemas de sessão.")
            
            # Gerar uma nova SECRET_KEY
            import secrets
            new_secret_key = secrets.token_hex(32)
            print(f"   Nova SECRET_KEY gerada: {new_secret_key[:20]}...")
            
            # Atualizar o arquivo .env
            env_file = '.env'
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                
                if 'SECRET_KEY=' in content:
                    # Substituir SECRET_KEY existente
                    import re
                    content = re.sub(r'SECRET_KEY=.*', f'SECRET_KEY={new_secret_key}', content)
                else:
                    # Adicionar SECRET_KEY
                    content += f'\nSECRET_KEY={new_secret_key}'
                
                with open(env_file, 'w') as f:
                    f.write(content)
                
                print(f"   ✅ SECRET_KEY atualizada no arquivo {env_file}")
                
            except FileNotFoundError:
                print(f"   ⚠️ Arquivo {env_file} não encontrado")
                print(f"   Adicione manualmente: SECRET_KEY={new_secret_key}")
        
        # Verificar configurações de sessão para produção
        if not app.config.get('DEBUG', False):
            print("\n🔒 Configurações para produção:")
            print("   SESSION_COOKIE_SECURE deve ser True em produção")
            print("   SESSION_COOKIE_HTTPONLY deve ser True")
            print("   SESSION_COOKIE_SAMESITE deve ser 'Lax' ou 'Strict'")
        
        # Verificar se há problemas com o banco de dados
        print("\n🗄️ Verificando banco de dados...")
        try:
            db.create_all()
            print("   ✅ Banco de dados OK")
            
            # Verificar usuário admin
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"   ✅ Usuário admin encontrado: {admin.username}")
                print(f"   ✅ Usuário ativo: {admin.is_active}")
            else:
                print("   ❌ Usuário admin não encontrado")
                
        except Exception as e:
            print(f"   ❌ Erro no banco de dados: {e}")
        
        print("\n📋 Recomendações:")
        print("1. Verifique se o SECRET_KEY está configurado corretamente")
        print("2. Em produção, certifique-se de que SESSION_COOKIE_SECURE=True")
        print("3. Verifique se o Nginx está configurado corretamente para sessões")
        print("4. Reinicie o serviço após as mudanças")

if __name__ == '__main__':
    fix_session_issues()
