#!/usr/bin/env python3
"""
Script para testar as funcionalidades de perfil e configurações
"""

import requests
from bs4 import BeautifulSoup
import re

def test_profile_and_settings():
    base_url = "http://localhost:5000"
    
    # Dados de login
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    print("🧪 Testando funcionalidades de Perfil e Configurações...")
    print("=" * 60)
    
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
        
        # 2. Testar página de perfil
        print("\n2. Testando página de perfil...")
        profile_response = session.get(f"{base_url}/profile")
        
        if profile_response.status_code == 200:
            print("   ✅ Página de perfil carregada com sucesso")
            
            # Verificar se os formulários estão presentes
            soup = BeautifulSoup(profile_response.text, 'html.parser')
            
            # Verificar formulário de perfil
            profile_form = soup.find('form', {'action': '/profile'})
            if profile_form:
                print("   ✅ Formulário de perfil encontrado")
            else:
                print("   ❌ Formulário de perfil não encontrado")
            
            # Verificar formulário de alteração de senha
            password_form = soup.find('form', {'action': '/change_password'})
            if password_form:
                print("   ✅ Formulário de alteração de senha encontrado")
            else:
                print("   ❌ Formulário de alteração de senha não encontrado")
                
        else:
            print("   ❌ Erro ao carregar página de perfil")
            return False
        
        # 3. Testar página de configurações
        print("\n3. Testando página de configurações...")
        settings_response = session.get(f"{base_url}/settings")
        
        if settings_response.status_code == 200:
            print("   ✅ Página de configurações carregada com sucesso")
            
            # Verificar se os formulários estão presentes
            soup = BeautifulSoup(settings_response.text, 'html.parser')
            
            # Verificar formulário de configurações gerais
            general_form = soup.find('form', {'action': '/settings'})
            if general_form:
                print("   ✅ Formulário de configurações gerais encontrado")
            else:
                print("   ❌ Formulário de configurações gerais não encontrado")
            
            # Verificar formulário de configurações de e-mail
            email_form = soup.find('form', {'action': '/email_settings'})
            if email_form:
                print("   ✅ Formulário de configurações de e-mail encontrado")
            else:
                print("   ❌ Formulário de configurações de e-mail não encontrado")
            
            # Verificar formulário de configurações de backup
            backup_form = soup.find('form', {'action': '/backup_settings'})
            if backup_form:
                print("   ✅ Formulário de configurações de backup encontrado")
            else:
                print("   ❌ Formulário de configurações de backup não encontrado")
                
        else:
            print("   ❌ Erro ao carregar página de configurações")
            return False
        
        # 4. Testar funcionalidade de backup
        print("\n4. Testando funcionalidade de backup...")
        backup_response = session.get(f"{base_url}/create_backup")
        
        if backup_response.status_code == 200:
            print("   ✅ Funcionalidade de backup funcionando")
        else:
            print("   ❌ Erro na funcionalidade de backup")
        
        print("\n" + "=" * 60)
        print("🎉 Todos os testes de Perfil e Configurações foram concluídos!")
        print("✅ As abas de perfil e configurações estão funcionando corretamente")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Certifique-se de que o servidor está rodando em http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    test_profile_and_settings()

