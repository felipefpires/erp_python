#!/usr/bin/env python3
"""
Script para migrar o banco de dados e adicionar o campo Instagram ao modelo Customer
"""

import sqlite3
import os

def migrate_instagram():
    db_path = 'instance/erp.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Iniciando migração para adicionar campo Instagram...")
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(customer)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'instagram' in columns:
            print("✅ Campo Instagram já existe na tabela customer")
            return True
        
        # Adicionar a coluna instagram
        cursor.execute("ALTER TABLE customer ADD COLUMN instagram VARCHAR(100)")
        
        # Commit das alterações
        conn.commit()
        
        print("✅ Campo Instagram adicionado com sucesso!")
        
        # Verificar se foi adicionado
        cursor.execute("PRAGMA table_info(customer)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'instagram' in columns:
            print("✅ Migração concluída com sucesso!")
            return True
        else:
            print("❌ Erro: Campo Instagram não foi adicionado")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = migrate_instagram()
    if success:
        print("\n🎉 Migração concluída! O campo Instagram foi adicionado ao modelo Customer.")
    else:
        print("\n💥 Falha na migração. Verifique os erros acima.")
