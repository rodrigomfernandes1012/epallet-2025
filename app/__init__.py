from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import os

# Inicializar extensões
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name=None):
    """Factory function para criar a aplicação Flask"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensões com a app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configurar login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Registrar blueprints
    from app.routes import auth, main, empresas, tipos_empresa, motoristas, vale_pallet, publico, logs, relatorios, webhook
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(empresas.bp)
    app.register_blueprint(tipos_empresa.bp)
    app.register_blueprint(motoristas.bp)
    app.register_blueprint(vale_pallet.bp)
    app.register_blueprint(publico.publico_bp)  # Rotas públicas (sem login)
    app.register_blueprint(logs.bp)
    app.register_blueprint(relatorios.bp)
    app.register_blueprint(webhook.webhook_bp)  # Webhook WhatsApp
    
    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    return app
