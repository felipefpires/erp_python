from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Determinar configuração
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Configuração
    app.config.from_object(config[config_name])
    
    # Inicialização das extensões
    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)
    CORS(app)
    
    # Configuração do login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Configurações de sessão para desenvolvimento
    if app.config.get('DEBUG', False):
        app.config['SESSION_COOKIE_SECURE'] = False
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Registro dos blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.crm import crm_bp
    from app.routes.inventory import inventory_bp
    from app.routes.finance import finance_bp
    from app.routes.schedule import schedule_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(crm_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(schedule_bp)
    
    # Criação das tabelas (apenas em desenvolvimento)
    if app.config.get('DEBUG', False):
        with app.app_context():
            db.create_all()
    
    return app
