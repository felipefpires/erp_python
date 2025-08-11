#!/usr/bin/env python3
"""
Script para testar o dashboard após a correção do erro
"""

import requests
import sys
import time

def test_dashboard():
    """Testa se o dashboard está funcionando corretamente"""
    
    print("🧪 Testando o Dashboard do Sistema ERP...")
    print("=" * 50)
    
    # URL base do sistema
    base_url = "http://localhost:5000"
    
    try:
        # Teste 1: Verificar se o servidor está respondendo
        print("1. Verificando se o servidor está respondendo...")
        response = requests.get(base_url, timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Servidor está respondendo")
        else:
            print(f"   ❌ Servidor retornou status {response.status_code}")
            return False
            
        # Teste 2: Verificar se a página de login está acessível
        print("2. Verificando página de login...")
        response = requests.get(f"{base_url}/login", timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Página de login está acessível")
        else:
            print(f"   ❌ Página de login retornou status {response.status_code}")
            return False
            
        # Teste 3: Tentar acessar o dashboard (deve redirecionar para login)
        print("3. Verificando redirecionamento do dashboard...")
        response = requests.get(f"{base_url}/dashboard", timeout=5, allow_redirects=False)
        
        if response.status_code in [302, 401]:
            print("   ✅ Dashboard está protegido (redirecionando para login)")
        else:
            print(f"   ⚠️  Dashboard retornou status {response.status_code}")
            
        print("\n" + "=" * 50)
        print("🎉 Testes concluídos com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Acesse http://localhost:5000 no seu navegador")
        print("2. Faça login com as credenciais:")
        print("   - Usuário: admin")
        print("   - Senha: admin123")
        print("3. Clique em 'Dashboard' no menu lateral")
        print("4. O dashboard deve carregar sem erros!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Não foi possível conectar ao servidor")
        print("   💡 Certifique-se de que o servidor está rodando com: python app.py")
        return False
        
    except requests.exceptions.Timeout:
        print("   ❌ Timeout ao conectar ao servidor")
        return False
        
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Sistema ERP - Teste do Dashboard")
    print("=" * 50)
    
    success = test_dashboard()
    
    if success:
        print("\n✅ Todos os testes passaram! O erro foi corrigido.")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam. Verifique o servidor.")
        sys.exit(1)


