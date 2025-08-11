#!/usr/bin/env python3
"""
Teste simples para verificar se o servidor está rodando
"""

import requests

def test_server():
    base_url = "http://localhost:5000"
    
    print("🔍 Testando se o servidor está rodando...")
    print(f"🌐 URL: {base_url}")
    
    try:
        # Tentar conectar ao servidor
        response = requests.get(base_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Servidor está rodando!")
            print(f"📄 Página carregada: {len(response.text)} caracteres")
            return True
        else:
            print(f"⚠️ Servidor respondeu com status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor Flask está rodando com: python app.py")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    test_server()

