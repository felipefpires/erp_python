#!/usr/bin/env python3
"""
Script para testar se os 4 erros do CRM foram corrigidos
"""

import requests
import time
from urllib.parse import urljoin

BASE_URL = "http://localhost:5000"

def test_login():
    """Faz login no sistema"""
    print("🔐 Testando login...")
    
    session = requests.Session()
    
    # Página de login
    response = session.get(urljoin(BASE_URL, "/auth/login"))
    if response.status_code != 200:
        print("❌ Erro ao acessar página de login")
        return None
    
    # Fazer login
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    response = session.post(urljoin(BASE_URL, "/auth/login"), data=login_data)
    if response.status_code != 200:
        print("❌ Erro no login")
        return None
    
    print("✅ Login realizado com sucesso")
    return session

def test_novo_cliente(session):
    """Testa a página de novo cliente (erro 1)"""
    print("\n👤 Testando página de novo cliente...")
    
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

def test_historico_vendas(session):
    """Testa a página de histórico de vendas (erro 2)"""
    print("\n📊 Testando página de histórico de vendas...")
    
    try:
        response = session.get(urljoin(BASE_URL, "/crm/sales"))
        if response.status_code == 200:
            print("✅ Página de histórico de vendas carregada com sucesso")
            return True
        else:
            print(f"❌ Erro {response.status_code} na página de histórico de vendas")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página de histórico de vendas: {e}")
        return False

def test_relatorios(session):
    """Testa a página de relatórios (erro 3)"""
    print("\n📈 Testando página de relatórios...")
    
    try:
        response = session.get(urljoin(BASE_URL, "/crm/reports"))
        if response.status_code == 200:
            print("✅ Página de relatórios carregada com sucesso")
            return True
        else:
            print(f"❌ Erro {response.status_code} na página de relatórios")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página de relatórios: {e}")
        return False

def test_agendamentos(session):
    """Testa a página de agendamentos (erro 4)"""
    print("\n📅 Testando página de agendamentos...")
    
    try:
        response = session.get(urljoin(BASE_URL, "/schedule/appointments"))
        if response.status_code == 200:
            print("✅ Página de agendamentos carregada com sucesso")
            return True
        else:
            print(f"❌ Erro {response.status_code} na página de agendamentos")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar página de agendamentos: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes dos 4 erros do CRM...")
    print("=" * 50)
    
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
    
    resultados.append(test_novo_cliente(session))
    resultados.append(test_historico_vendas(session))
    resultados.append(test_relatorios(session))
    resultados.append(test_agendamentos(session))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES")
    print("=" * 50)
    
    erros = [
        "Novo Cliente (form undefined)",
        "Histórico de Vendas (QueryPagination len)",
        "Relatórios (summary undefined)", 
        "Agendamentos (template not found)"
    ]
    
    for i, (erro, resultado) in enumerate(zip(erros, resultados), 1):
        status = "✅ CORRIGIDO" if resultado else "❌ AINDA COM ERRO"
        print(f"{i}. {erro}: {status}")
    
    total_corrigidos = sum(resultados)
    print(f"\n🎯 Total: {total_corrigidos}/4 erros corrigidos")
    
    if total_corrigidos == 4:
        print("🎉 Todos os erros foram corrigidos com sucesso!")
    else:
        print("⚠️  Alguns erros ainda precisam ser corrigidos.")

if __name__ == "__main__":
    main()

