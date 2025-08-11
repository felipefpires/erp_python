#!/usr/bin/env python3
"""
Script para verificar se o usuário admin existe no banco
"""

import sqlite3

def check_admin_user():
    db_path = 'instance/erp.db'
    
    print("🔍 Verificando usuário admin no banco...")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ Conectado ao banco")
        
        # Verificar se a tabela user existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("❌ Tabela 'user' não encontrada")
            return False
        
        # Verificar estrutura da tabela user
        print("\n📋 Estrutura da tabela user:")
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Verificar se existe usuário admin
        print("\n👤 Verificando usuário admin:")
        cursor.execute("SELECT id, username, email, role, is_active FROM user WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            print("✅ Usuário admin encontrado:")
            print(f"   ID: {admin_user[0]}")
            print(f"   Username: {admin_user[1]}")
            print(f"   Email: {admin_user[2]}")
            print(f"   Role: {admin_user[3]}")
            print(f"   Ativo: {admin_user[4]}")
        else:
            print("❌ Usuário admin não encontrado")
            
            # Listar todos os usuários
            cursor.execute("SELECT id, username, email, role FROM user")
            users = cursor.fetchall()
            print(f"\n📋 Usuários existentes ({len(users)}):")
            for user in users:
                print(f"   - {user[1]} ({user[2]}) - {user[3]}")
        
        # Contar total de usuários
        cursor.execute("SELECT COUNT(*) FROM user")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total de usuários no banco: {total}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a verificação: {e}")
        return False

if __name__ == "__main__":
    check_admin_user()
