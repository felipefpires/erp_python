#!/usr/bin/env python3
"""
Script para verificar todos os índices da tabela customer
"""

import sqlite3

def check_indexes():
    db_path = 'instance/erp.db'
    
    print("🔍 Verificando índices da tabela customer...")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ Conectado ao banco")
        
        # Verificar todos os índices da tabela customer
        print("\n📋 Todos os índices da tabela customer:")
        cursor.execute("PRAGMA index_list(customer)")
        indexes = cursor.fetchall()
        
        for idx in indexes:
            index_name = idx[1]
            is_unique = idx[2]
            print(f"   - {index_name} (UNIQUE: {is_unique})")
            
            # Verificar colunas do índice
            cursor.execute(f"PRAGMA index_info({index_name})")
            index_info = cursor.fetchall()
            for info in index_info:
                col_index = info[1]
                col_name = info[2]
                print(f"     Coluna {col_index}: {col_name}")
        
        # Verificar se há algum índice específico para email
        print("\n🔍 Verificando índices específicos para email:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND sql LIKE '%email%'")
        email_indexes = cursor.fetchall()
        
        if email_indexes:
            for idx in email_indexes:
                print(f"   - {idx[0]}")
        else:
            print("   Nenhum índice específico para email encontrado")
        
        # Tentar inserir um cliente com email duplicado para testar
        print("\n🧪 Testando inserção com email duplicado...")
        try:
            cursor.execute("""
                INSERT INTO customer (name, email, phone, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                'Teste Duplicado',
                'felipefpires74@gmail.com',  # Email que já existe
                '(11) 99999-9999',
                'active',
                '2025-08-10 20:00:00',
                '2025-08-10 20:00:00'
            ))
            conn.commit()
            print("   ✅ Inserção com email duplicado funcionou!")
            
            # Remover o registro de teste
            cursor.execute("DELETE FROM customer WHERE name = 'Teste Duplicado'")
            conn.commit()
            print("   ✅ Registro de teste removido")
            
        except sqlite3.IntegrityError as e:
            print(f"   ❌ Erro de integridade: {e}")
        
        conn.close()
        print("\n✅ Verificação concluída!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a verificação: {e}")
        return False

if __name__ == "__main__":
    check_indexes()
