#!/usr/bin/env python3
"""
Script para migrar o banco de dados e remover a restrição UNIQUE do campo email
"""

import sqlite3
import os

def migrate_email_unique():
    db_path = 'instance/erp.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Iniciando migração para remover restrição UNIQUE do email...")
        
        # Verificar se a restrição UNIQUE existe
        cursor.execute("PRAGMA index_list(customer)")
        indexes = cursor.fetchall()
        
        # Procurar por índice UNIQUE no email
        email_unique_index = None
        for index in indexes:
            index_name = index[1]
            if 'email' in index_name.lower() and 'unique' in index_name.lower():
                email_unique_index = index_name
                break
        
        if email_unique_index:
            print(f"📋 Encontrado índice UNIQUE: {email_unique_index}")
            
            # Remover o índice UNIQUE
            cursor.execute(f"DROP INDEX {email_unique_index}")
            print("✅ Índice UNIQUE removido com sucesso!")
        else:
            print("ℹ️ Nenhum índice UNIQUE encontrado para o campo email")
        
        # Commit das alterações
        conn.commit()
        
        print("✅ Migração concluída com sucesso!")
        return True
            
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = migrate_email_unique()
    if success:
        print("\n🎉 Migração concluída! A restrição UNIQUE foi removida do campo email.")
    else:
        print("\n💥 Falha na migração. Verifique os erros acima.")

