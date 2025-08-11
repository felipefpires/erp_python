#!/usr/bin/env python3
"""
Script para testar a correção dos 5 erros do módulo de estoque
"""

import requests
import time
from urllib.parse import urljoin

# Configurações
BASE_URL = "http://localhost:5000"
LOGIN_URL = urljoin(BASE_URL, "/auth/login")
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_login():
    """Testa o login do administrador"""
    print("🔐 Testando login...")
    
    session = requests.Session()
    
    try:
        # Fazer login
        login_data = {
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD
        }
        
        response = session.post(LOGIN_URL, data=login_data, allow_redirects=False)
        
        if response.status_code == 302:  # Redirect após login bem-sucedido
            print("✅ Login realizado com sucesso")
            return session
        else:
            print(f"❌ Falha no login. Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        return None

def test_movimentos(session):
    """Testa a página de movimentações (erro 1)"""
    print("\n📦 Testando página de movimentações...")
    
    try:
        response = session.get(urljoin(BASE_URL, "/inventory/movements"))
        if response.status_code == 200:
            print("✅ Página de movimentações carregada com sucesso")
            return True
        else:
            print(f"❌ Erro {response.status_code} na página de movimentações")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página de movimentações: {e}")
        return False

def test_relatorios_estoque(session):
    """Testa a página de relatórios de estoque (erro 2)"""
    print("\n📊 Testando página de relatórios de estoque...")
    
    try:
        response = session.get(urljoin(BASE_URL, "/inventory/reports"))
        if response.status_code == 200:
            print("✅ Página de relatórios de estoque carregada com sucesso")
            return True
        else:
            print(f"❌ Erro {response.status_code} na página de relatórios de estoque")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página de relatórios de estoque: {e}")
        return False

def test_novo_movimento(session):
    """Testa a página de novo movimento (erro 3)"""
    print("\n➕ Testando página de novo movimento...")
    
    try:
        response = session.get(urljoin(BASE_URL, "/inventory/movements/new"))
        if response.status_code == 200:
            print("✅ Página de novo movimento carregada com sucesso")
            return True
        else:
            print(f"❌ Erro {response.status_code} na página de novo movimento")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página de novo movimento: {e}")
        return False

def test_categorias(session):
    """Testa a página de categorias (erro 4)"""
    print("\n🏷️ Testando página de categorias...")
    
    try:
        response = session.get(urljoin(BASE_URL, "/inventory/categories"))
        if response.status_code == 200:
            print("✅ Página de categorias carregada com sucesso")
            return True
        else:
            print(f"❌ Erro {response.status_code} na página de categorias")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página de categorias: {e}")
        return False

def test_novo_cliente_2(session):
    """Testa a página de novo cliente (erro 5)"""
    print("\n👤 Testando página de novo cliente (segundo erro)...")
    
    try:
        response = session.get(urljoin(BASE_URL, "/crm/customers/new"))
        if response.status_code == 200:
            print("✅ Página de novo cliente carregada com sucesso")
            return True
        else:
            print(f"❌ Erro {response.status_code} na página de novo cliente")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página de novo cliente: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes dos 5 erros do módulo de estoque...")
    print("=" * 60)
    
    # Aguardar o servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(3)
    
    # Fazer login
    session = test_login()
    if not session:
        print("❌ Não foi possível fazer login. Abortando testes.")
        return
    
    # Testar cada erro
    resultados = []
    
    resultados.append(test_movimentos(session))
    resultados.append(test_relatorios_estoque(session))
    resultados.append(test_novo_movimento(session))
    resultados.append(test_categorias(session))
    resultados.append(test_novo_cliente_2(session))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    erros = [
        "Movimentações (pagination undefined)",
        "Relatórios de Estoque (summary undefined)",
        "Novo Movimento (now undefined)",
        "Categorias (pagination undefined)",
        "Novo Cliente 2 (form fields undefined)"
    ]
    
    for i, (erro, resultado) in enumerate(zip(erros, resultados), 1):
        status = "✅ CORRIGIDO" if resultado else "❌ AINDA COM ERRO"
        print(f"{i}. {erro}: {status}")
    
    total_corrigidos = sum(resultados)
    print(f"\n🎯 Total: {total_corrigidos}/5 erros corrigidos")
    
    if total_corrigidos == 5:
        print("🎉 Todos os erros foram corrigidos com sucesso!")
    else:
        print("⚠️  Alguns erros ainda precisam ser corrigidos.")

if __name__ == "__main__":
    main()

