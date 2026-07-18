import os
from flask import Flask

def create_app():
    """Fábrica de aplicação para inicialização limpa do Flask."""
    # Obtém o diretório raiz do projeto (acima de src/)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'), 
                static_folder=os.path.join(base_dir, 'static'))
    
    app.secret_key = "chave_secreta_para_desenvolvimento_local"

    # Registro de Blueprints
    from .rotas import main_bp
    app.register_blueprint(main_bp)

    # Injeção de headers anti-cache para ambiente de desenvolvimento rápido
    @app.after_request
    def remove_cache(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return app
