#!/usr/bin/env python3
"""
Teste para verificar se a página web de cadastro de clientes está funcionando
"""

import requests

def test_web_customer():
    base_url = "http://localhost:5000"
    
    print("🌐 Testando página web de cadastro de clientes...")
    print("=" * 50)
    
    try:
        # 1. Testar página inicial
        print("1. Testando página inicial...")
        response = requests.get(base_url, timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Página inicial carregada")
        else:
            print(f"   ❌ Erro na página inicial (Status: {response.status_code})")
            return False
        
        # 2. Testar página de login
        print("\n2. Testando página de login...")
        login_response = requests.get(f"{base_url}/login", timeout=5)
        
        if login_response.status_code == 200:
            print("   ✅ Página de login carregada")
        else:
            print(f"   ❌ Erro na página de login (Status: {login_response.status_code})")
            return False
        
        # 3. Fazer login
        print("\n3. Fazendo login...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        session = requests.Session()
        auth_response = session.post(f"{base_url}/login", data=login_data, timeout=5)
        
        if auth_response.status_code == 302:  # Redirecionamento após login
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Erro no login (Status: {auth_response.status_code})")
            return False
        
        # 4. Testar página de clientes
        print("\n4. Testando página de clientes...")
        customers_response = session.get(f"{base_url}/crm/customers", timeout=5)
        
        if customers_response.status_code == 200:
            print("   ✅ Página de clientes carregada")
        else:
            print(f"   ❌ Erro na página de clientes (Status: {customers_response.status_code})")
            return False
        
        # 5. Testar página de novo cliente
        print("\n5. Testando página de novo cliente...")
        new_customer_response = session.get(f"{base_url}/crm/customers/new", timeout=5)
        
        if new_customer_response.status_code == 200:
            print("   ✅ Página de novo cliente carregada")
            
            # Verificar se a página contém o campo Instagram
            if 'instagram' in new_customer_response.text.lower():
                print("   ✅ Campo Instagram encontrado na página")
            else:
                print("   ⚠️ Campo Instagram não encontrado na página")
        else:
            print(f"   ❌ Erro na página de novo cliente (Status: {new_customer_response.status_code})")
            return False
        
        print("\n🎉 Todos os testes web passaram com sucesso!")
        print("📝 Agora você pode testar manualmente:")
        print("   1. Acesse: http://localhost:5000")
        print("   2. Faça login com: admin / admin123")
        print("   3. Vá para CRM > Clientes > Novo Cliente")
        print("   4. Teste criar um cliente (apenas o nome é obrigatório)")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor Flask está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    test_web_customer()
