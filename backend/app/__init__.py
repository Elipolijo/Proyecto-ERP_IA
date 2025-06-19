# backend/app/__init__.py

from flask import Flask
from .database import mysql
from .routes.main import main_bp
from .routes.productos import productos_bp


def create_app():
    app = Flask(__name__)

    # Configuración de conexión a la base de datos
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'polijo'
    app.config['MYSQL_PASSWORD'] = '1234'
    app.config['MYSQL_DB'] = 'inventario_ia'

    # Inicializar extensión MySQL
    mysql.init_app(app)

    # Registrar las rutas
    app.register_blueprint(main_bp)
    app.register_blueprint(productos_bp) 

    return app
