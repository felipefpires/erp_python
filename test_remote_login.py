#!/usr/bin/env python3
"""
Script para testar login no servidor remoto
"""

import requests
from bs4 import BeautifulSoup
import re

def test_remote_login():
    base_url = "http://192.168.18.191"
    session = requests.Session()
    
    print("🔍 Testando Login no Servidor Remoto")
    print("=" * 50)
    print(f"🌐 URL: {base_url}")
    
    try:
        # 1. Acessar página de login
        print("\n1️⃣ Acessando página de login...")
        response = session.get(f"{base_url}/login")
        
        if response.status_code == 200:
            print("✅ Página de login acessada com sucesso")
            
            # Verificar se há mensagens de erro
            soup = BeautifulSoup(response.text, 'html.parser')
            error_messages = soup.find_all(class_='alert-danger')
            if error_messages:
                print(f"⚠️ Mensagens de erro encontradas: {[msg.get_text().strip() for msg in error_messages]}")
            
            # Verificar se o formulário existe
            form = soup.find('form')
            if form:
                print("✅ Formulário de login encontrado")
                print(f"   Método: {form.get('method', 'POST')}")
                print(f"   Action: {form.get('action', '')}")
            else:
                print("❌ Formulário de login não encontrado")
                return
                
        else:
            print(f"❌ Erro ao acessar página de login: {response.status_code}")
            return
        
        # 2. Tentar fazer login
        print("\n2️⃣ Tentando fazer login...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        print(f"📊 Status da resposta: {response.status_code}")
        print(f"📋 Headers de redirecionamento:")
        for header, value in response.headers.items():
            if 'location' in header.lower():
                print(f"   {header}: {value}")
        
        # 3. Verificar se foi redirecionado
        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers.get('Location', '')
            print(f"🔄 Redirecionamento para: {redirect_url}")
            
            # Seguir o redirecionamento
            if redirect_url.startswith('/'):
                redirect_url = base_url + redirect_url
            
            print(f"🔗 URL completa: {redirect_url}")
            
            response = session.get(redirect_url)
            print(f"📊 Status após redirecionamento: {response.status_code}")
            
            # Verificar se chegou no dashboard
            if 'dashboard' in response.url.lower() or 'dashboard' in response.text.lower():
                print("✅ Login bem-sucedido! Redirecionado para o dashboard")
            else:
                print("⚠️ Redirecionado, mas não para o dashboard")
                print(f"   URL final: {response.url}")
                
                # Verificar se há mensagens de erro
                soup = BeautifulSoup(response.text, 'html.parser')
                error_messages = soup.find_all(class_='alert-danger')
                if error_messages:
                    print(f"❌ Mensagens de erro: {[msg.get_text().strip() for msg in error_messages]}")
                
        else:
            print("❌ Não houve redirecionamento após login")
            
            # Verificar se há mensagens de erro
            soup = BeautifulSoup(response.text, 'html.parser')
            error_messages = soup.find_all(class_='alert-danger')
            if error_messages:
                print(f"❌ Mensagens de erro: {[msg.get_text().strip() for msg in error_messages]}")
            
            # Verificar se ainda está na página de login
            if 'login' in response.url.lower():
                print("⚠️ Ainda na página de login após tentativa de autenticação")
        
        # 4. Verificar cookies de sessão
        print(f"\n🍪 Cookies de sessão:")
        for cookie in session.cookies:
            print(f"   {cookie.name}: {cookie.value[:20]}...")
        
        # 5. Testar acesso direto ao dashboard
        print(f"\n3️⃣ Testando acesso direto ao dashboard...")
        response = session.get(f"{base_url}/dashboard")
        print(f"📊 Status do dashboard: {response.status_code}")
        
        if response.status_code == 200:
            if 'login' in response.url.lower():
                print("❌ Redirecionado para login ao tentar acessar dashboard")
            else:
                print("✅ Dashboard acessível após login")
        else:
            print(f"❌ Erro ao acessar dashboard: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão: Não foi possível conectar ao servidor")
    except requests.exceptions.Timeout:
        print("❌ Timeout: Servidor não respondeu a tempo")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == '__main__':
    test_remote_login()
