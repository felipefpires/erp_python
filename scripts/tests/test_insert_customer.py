#!/usr/bin/env python3
"""
Teste direto no banco para inserir um cliente
"""

import sqlite3
from datetime import datetime

def test_insert_customer():
    db_path = 'instance/erp.db'
    
    print("🧪 Testando inserção direta de cliente no banco...")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ Conectado ao banco")
        
        # Dados do cliente de teste
        customer_data = {
            'name': 'Cliente Teste Direto',
            'email': 'teste@teste.com',
            'phone': '(11) 99999-9999',
            'instagram': '@cliente_teste_direto',
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Inserir cliente
        print("📝 Inserindo cliente...")
        cursor.execute("""
            INSERT INTO customer (name, email, phone, instagram, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_data['name'],
            customer_data['email'],
            customer_data['phone'],
            customer_data['instagram'],
            customer_data['status'],
            customer_data['created_at'],
            customer_data['updated_at']
        ))
        
        # Confirmar a inserção
        conn.commit()
        print("✅ Cliente inserido com sucesso!")
        
        # Verificar se foi inserido
        cursor.execute("SELECT id, name, email, instagram FROM customer WHERE name = ?", (customer_data['name'],))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Cliente encontrado no banco:")
            print(f"   ID: {result[0]}")
            print(f"   Nome: {result[1]}")
            print(f"   Email: {result[2]}")
            print(f"   Instagram: {result[3]}")
        else:
            print("❌ Cliente não foi encontrado após inserção")
        
        # Contar total de clientes
        cursor.execute("SELECT COUNT(*) FROM customer")
        total = cursor.fetchone()[0]
        print(f"📊 Total de clientes no banco: {total}")
        
        conn.close()
        print("\n🎉 Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    test_insert_customer()
