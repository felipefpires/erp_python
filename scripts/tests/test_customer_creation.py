#!/usr/bin/env python3
"""
Script para testar a criação de clientes
"""

import requests
from bs4 import BeautifulSoup
import re

def test_customer_creation():
    base_url = "http://localhost:5000"
    
    # Dados de login
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    print("🧪 Testando criação de cliente...")
    print("=" * 50)
    
    # Criar sessão
    session = requests.Session()
    
    try:
        # 1. Fazer login
        print("1. Fazendo login...")
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print("   ❌ Erro no login")
            return False
        
        # 2. Acessar página de novo cliente
        print("\n2. Acessando página de novo cliente...")
        new_customer_response = session.get(f"{base_url}/crm/customers/new")
        
        if new_customer_response.status_code == 200:
            print("   ✅ Página de novo cliente carregada")
        else:
            print("   ❌ Erro ao carregar página de novo cliente")
            return False
        
        # 3. Tentar criar um cliente
        print("\n3. Criando cliente de teste...")
        customer_data = {
            'name': 'Cliente Teste',
            'email': 'teste@teste.com',
            'phone': '(11) 99999-9999',
            'instagram': '@cliente_teste',
            'status': 'active'
        }
        
        create_response = session.post(f"{base_url}/crm/customers/new", data=customer_data)
        
        if create_response.status_code == 302:  # Redirecionamento após sucesso
            print("   ✅ Cliente criado com sucesso!")
            
            # Verificar se foi redirecionado para a lista de clientes
            if 'customers' in create_response.headers.get('Location', ''):
                print("   ✅ Redirecionamento correto para lista de clientes")
            else:
                print("   ⚠️ Redirecionamento inesperado")
        else:
            print(f"   ❌ Erro ao criar cliente (Status: {create_response.status_code})")
            
            # Verificar se há mensagens de erro
            soup = BeautifulSoup(create_response.text, 'html.parser')
            error_messages = soup.find_all(class_='alert-danger')
            if error_messages:
                for error in error_messages:
                    print(f"   ❌ Erro: {error.get_text().strip()}")
            
            return False
        
        print("\n🎉 Teste concluído com sucesso!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor Flask está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    test_customer_creation()

