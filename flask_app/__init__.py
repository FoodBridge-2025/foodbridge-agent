from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Configuration settings
    app.config.from_pyfile('config.py')
    
    # Import and register routes
    from . import routes
    app.register_blueprint(routes.bp)
    
    return app