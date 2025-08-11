#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do sistema ERP
"""

from app import create_app, db
from app.models.user import User
from app.models.crm import Customer
from app.models.inventory import Product, Category
from app.models.finance import Account, Transaction
from app.models.schedule import Event, Appointment
from datetime import datetime, timedelta

def test_system():
    app = create_app()
    
    with app.app_context():
        print("🧪 Testando o Sistema ERP...")
        print("=" * 50)
        
        # Teste 1: Verificar se o banco de dados está funcionando
        print("1. Testando conexão com banco de dados...")
        try:
            db.engine.execute("SELECT 1")
            print("   ✅ Conexão com banco de dados OK")
        except Exception as e:
            print(f"   ❌ Erro na conexão com banco: {e}")
            return
        
        # Teste 2: Verificar se as tabelas existem
        print("2. Verificando tabelas...")
        tables = ['user', 'customer', 'product', 'category', 'account', 'transaction', 'event', 'appointment']
        for table in tables:
            try:
                db.engine.execute(f"SELECT COUNT(*) FROM {table}")
                print(f"   ✅ Tabela {table} OK")
            except Exception as e:
                print(f"   ❌ Erro na tabela {table}: {e}")
        
        # Teste 3: Verificar dados de exemplo
        print("3. Verificando dados de exemplo...")
        
        # Usuários
        users = User.query.all()
        print(f"   👥 Usuários cadastrados: {len(users)}")
        
        # Clientes
        customers = Customer.query.all()
        print(f"   👤 Clientes cadastrados: {len(customers)}")
        
        # Produtos
        products = Product.query.all()
        print(f"   📦 Produtos cadastrados: {len(products)}")
        
        # Categorias
        categories = Category.query.all()
        print(f"   🏷️  Categorias cadastradas: {len(categories)}")
        
        # Contas
        accounts = Account.query.all()
        print(f"   🏦 Contas cadastradas: {len(accounts)}")
        
        # Transações
        transactions = Transaction.query.all()
        print(f"   💰 Transações cadastradas: {len(transactions)}")
        
        # Eventos
        events = Event.query.all()
        print(f"   📅 Eventos cadastrados: {len(events)}")
        
        # Agendamentos
        appointments = Appointment.query.all()
        print(f"   🕐 Agendamentos cadastrados: {len(appointments)}")
        
        print("\n" + "=" * 50)
        print("🎉 Teste concluído!")
        print("\n📋 Resumo do Sistema:")
        print(f"   • Total de usuários: {len(users)}")
        print(f"   • Total de clientes: {len(customers)}")
        print(f"   • Total de produtos: {len(products)}")
        print(f"   • Total de categorias: {len(categories)}")
        print(f"   • Total de contas: {len(accounts)}")
        print(f"   • Total de transações: {len(transactions)}")
        print(f"   • Total de eventos: {len(events)}")
        print(f"   • Total de agendamentos: {len(appointments)}")
        
        print("\n🚀 Para acessar o sistema:")
        print("   1. Execute: python app.py")
        print("   2. Acesse: http://localhost:5000")
        print("   3. Login: admin / admin123")

if __name__ == '__main__':
    test_system()


