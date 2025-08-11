#!/usr/bin/env python3
"""
Script para migrar o modelo Category e adicionar os novos campos
"""

from app import create_app, db
from app.models.inventory import Category
from sqlalchemy import text

def migrate_categories():
    """Migra o modelo Category para incluir os novos campos"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Iniciando migração do modelo Category...")
        
        try:
            # Verificar se as colunas já existem
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('category')]
            
            print(f"📋 Colunas existentes: {existing_columns}")
            
            # Adicionar coluna slug se não existir
            if 'slug' not in existing_columns:
                print("➕ Adicionando coluna 'slug'...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE category ADD COLUMN slug VARCHAR(50)"))
                    conn.commit()
                print("✅ Coluna 'slug' adicionada com sucesso")
            else:
                print("ℹ️  Coluna 'slug' já existe")
            
            # Adicionar coluna is_active se não existir
            if 'is_active' not in existing_columns:
                print("➕ Adicionando coluna 'is_active'...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE category ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
                    conn.commit()
                print("✅ Coluna 'is_active' adicionada com sucesso")
            else:
                print("ℹ️  Coluna 'is_active' já existe")
            
            # Atualizar categorias existentes
            print("🔄 Atualizando categorias existentes...")
            categories = Category.query.all()
            
            for category in categories:
                # Gerar slug se não existir
                if not category.slug:
                    category.slug = category.name.lower().replace(' ', '-').replace('_', '-')
                
                # Definir is_active como True se não existir
                if not hasattr(category, 'is_active') or category.is_active is None:
                    category.is_active = True
            
            db.session.commit()
            print(f"✅ {len(categories)} categorias atualizadas")
            
            print("🎉 Migração concluída com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro durante a migração: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    migrate_categories()
