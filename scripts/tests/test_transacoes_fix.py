#!/usr/bin/env python3
"""
Script para testar se o erro na aba transações foi corrigido
"""

import requests
import json

def test_transactions_page():
    """Testa se a página de transações carrega sem erros"""
    
    # URL base do sistema
    base_url = "http://localhost:5000"
    
    # Dados de login
    login_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        print("🔐 Fazendo login...")
        
        # Fazer login
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login realizado com sucesso")
            
            # Testar acesso à página de transações
            print("📊 Testando página de transações...")
            transactions_response = session.get(f"{base_url}/finance/transactions")
            
            if transactions_response.status_code == 200:
                print("✅ Página de transações carregou com sucesso!")
                
                # Verificar se há erros no conteúdo
                content = transactions_response.text
                if "error" in content.lower() or "exception" in content.lower():
                    print("❌ Página carregou mas contém erros no conteúdo")
                    return False
                else:
                    print("✅ Página de transações funcionando corretamente")
                    return True
            else:
                print(f"❌ Erro ao acessar página de transações: {transactions_response.status_code}")
                return False
                
        else:
            print(f"❌ Erro no login: {login_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Certifique-se de que o servidor está rodando.")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testando correção do erro na aba transações...")
    print("=" * 50)
    
    success = test_transactions_page()
    
    print("=" * 50)
    if success:
        print("🎉 Teste concluído com sucesso! O erro foi corrigido.")
    else:
        print("💥 Teste falhou. O erro ainda persiste.")

