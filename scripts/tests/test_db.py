#!/usr/bin/env python3
"""
Script para testar o banco de dados
"""

import sqlite3
import os

def test_database():
    db_path = 'instance/erp.db'
    
    print("🔍 Testando banco de dados...")
    print(f"📁 Caminho do banco: {db_path}")
    
    # Verificar se o arquivo existe
    if os.path.exists(db_path):
        print("✅ Arquivo do banco encontrado")
    else:
        print("❌ Arquivo do banco não encontrado")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ Conexão estabelecida com sucesso")
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Tabelas encontradas ({len(tables)}):")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Verificar estrutura da tabela customer
        if any('customer' in table[0].lower() for table in tables):
            print("\n🔍 Verificando estrutura da tabela customer:")
            cursor.execute("PRAGMA table_info(customer)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[1]} ({col[2]}) - NOT NULL: {col[3]} - UNIQUE: {col[5]}")
        
        # Verificar índices da tabela customer
        print("\n🔍 Verificando índices da tabela customer:")
        cursor.execute("PRAGMA index_list(customer)")
        indexes = cursor.fetchall()
        for idx in indexes:
            print(f"   - {idx[1]} (UNIQUE: {idx[2]})")
        
        conn.close()
        print("\n✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    test_database()

