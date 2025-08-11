#!/usr/bin/env python3
"""
Script para remover o índice único do email
"""

import sqlite3

def remove_email_index():
    db_path = 'instance/erp.db'
    
    print("🔧 Removendo índice único do email...")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ Conectado ao banco")
        
        # Verificar se o índice existe
        print("\n🔍 Verificando índice atual:")
        cursor.execute("PRAGMA index_list(customer)")
        indexes = cursor.fetchall()
        
        email_index = None
        for idx in indexes:
            if idx[1] == 'sqlite_autoindex_customer_1':
                email_index = idx[1]
                print(f"   - Encontrado: {idx[1]} (UNIQUE: {idx[2]})")
                break
        
        if email_index:
            print(f"\n🗑️ Removendo índice: {email_index}")
            
            # Remover o índice
            cursor.execute(f"DROP INDEX {email_index}")
            conn.commit()
            print("   ✅ Índice removido com sucesso!")
            
            # Verificar se foi removido
            cursor.execute("PRAGMA index_list(customer)")
            remaining_indexes = cursor.fetchall()
            print(f"\n📋 Índices restantes ({len(remaining_indexes)}):")
            for idx in remaining_indexes:
                print(f"   - {idx[1]} (UNIQUE: {idx[2]})")
            
            # Testar inserção com email duplicado
            print("\n🧪 Testando inserção com email duplicado...")
            try:
                cursor.execute("""
                    INSERT INTO customer (name, email, phone, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    'Teste Final',
                    'felipefpires74@gmail.com',
                    '(11) 99999-9999',
                    'active',
                    '2025-08-10 20:00:00',
                    '2025-08-10 20:00:00'
                ))
                conn.commit()
                print("   ✅ Inserção com email duplicado funcionou!")
                
                # Remover o registro de teste
                cursor.execute("DELETE FROM customer WHERE name = 'Teste Final'")
                conn.commit()
                print("   ✅ Registro de teste removido")
                
            except sqlite3.IntegrityError as e:
                print(f"   ❌ Ainda há erro de integridade: {e}")
        else:
            print("   ⚠️ Índice não encontrado")
        
        conn.close()
        print("\n✅ Operação concluída!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a operação: {e}")
        return False

if __name__ == "__main__":
    remove_email_index()
