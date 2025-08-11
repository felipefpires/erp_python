#!/usr/bin/env python3
"""
Script para testar se o erro na aba categorias foi corrigido
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

def test_categorias_page(session):
    """Testa a página de categorias"""
    print("\n🏷️ Testando página de categorias...")
    
    try:
        response = session.get(urljoin(BASE_URL, "/inventory/categories"))
        if response.status_code == 200:
            print("✅ Página de categorias carregada com sucesso")
            
            # Verificar se há erros no conteúdo
            if "error" in response.text.lower() or "exception" in response.text.lower():
                print("⚠️  Possível erro detectado no conteúdo da página")
                return False
            else:
                print("✅ Nenhum erro detectado no conteúdo")
                return True
        else:
            print(f"❌ Erro {response.status_code} na página de categorias")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página de categorias: {e}")
        return False

def test_new_category_page(session):
    """Testa a página de nova categoria"""
    print("\n➕ Testando página de nova categoria...")
    
    try:
        response = session.get(urljoin(BASE_URL, "/inventory/categories/new"))
        if response.status_code == 200:
            print("✅ Página de nova categoria carregada com sucesso")
            return True
        else:
            print(f"❌ Erro {response.status_code} na página de nova categoria")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página de nova categoria: {e}")
        return False

def test_edit_category_page(session):
    """Testa a página de editar categoria (se houver categorias)"""
    print("\n✏️ Testando página de editar categoria...")
    
    try:
        # Primeiro, verificar se há categorias
        categories_response = session.get(urljoin(BASE_URL, "/inventory/categories"))
        if categories_response.status_code == 200:
            # Tentar acessar a primeira categoria (ID 1)
            response = session.get(urljoin(BASE_URL, "/inventory/categories/1/edit"))
            if response.status_code == 200:
                print("✅ Página de editar categoria carregada com sucesso")
                return True
            elif response.status_code == 404:
                print("ℹ️  Nenhuma categoria encontrada para editar (404)")
                return True  # Não é um erro, apenas não há categorias
            else:
                print(f"❌ Erro {response.status_code} na página de editar categoria")
                return False
        else:
            print(f"❌ Erro ao verificar categorias: {categories_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página de editar categoria: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Testando correção do erro na aba categorias...")
    print("=" * 60)
    
    # Aguardar o servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(3)
    
    # Fazer login
    session = test_login()
    if not session:
        print("❌ Não foi possível fazer login. Abortando testes.")
        return
    
    # Testar cada funcionalidade
    resultados = []
    
    resultados.append(test_categorias_page(session))
    resultados.append(test_new_category_page(session))
    resultados.append(test_edit_category_page(session))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    testes = [
        "Página de Categorias",
        "Página de Nova Categoria", 
        "Página de Editar Categoria"
    ]
    
    for i, (teste, resultado) in enumerate(zip(testes, resultados), 1):
        status = "✅ FUNCIONANDO" if resultado else "❌ COM ERRO"
        print(f"{i}. {teste}: {status}")
    
    total_funcionando = sum(resultados)
    print(f"\n🎯 Total: {total_funcionando}/3 funcionalidades funcionando")
    
    if total_funcionando == 3:
        print("🎉 Todos os testes passaram! O erro foi corrigido com sucesso!")
    else:
        print("⚠️  Alguns problemas ainda precisam ser corrigidos.")

if __name__ == "__main__":
    main()

