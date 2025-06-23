# backend/app/__init__.py

#--> Aquí se van importante las ruta 
from flask import Flask
from .database import mysql

def create_app():
    app = Flask(__name__)

    # Configuración de conexión a la base de datos
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'polijo'
    app.config['MYSQL_PASSWORD'] = '1234'
    app.config['MYSQL_DB'] = 'inventario_ia'

    # Inicializar extensión MySQL
    mysql.init_app(app)

    from .routes.main import main_bp
    from .routes.productos import productos_bp
    from .routes.categorias import categorias_bp
    from .routes.proveedores import proveedores_bp
    from .routes.clientes import clientes_bp
    from .routes.entrada_stock import entrada_stock_bp
    from .routes.facturas import facturas_bp
    from app.routes.reportes import reportes_bp



    # Registrar las rutas
    app.register_blueprint(main_bp)
    app.register_blueprint(productos_bp) 
    app.register_blueprint(categorias_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(entrada_stock_bp)    # Configuración adicional
    app.register_blueprint(facturas_bp) 
    app.register_blueprint(reportes_bp)# Configuración adicional
    

    return app
