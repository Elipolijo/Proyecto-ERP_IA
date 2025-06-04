
#EN MAIN SE VAN A DEFINIR LAS RUTAS 


# backend/app/routes/main.py
from flask import Blueprint, jsonify
from app.database import mysql

# Creamos el "blueprint" para las rutas principales
main_bp = Blueprint('main', __name__)

# Ruta de prueba: /ping
@main_bp.route('/test-db')   # aquí GET devuelve al al cliente
def test_db():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DATABASE();")
    db_actual = cursor.fetchone()
    
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    cursor.close()
   
    return jsonify({"base_de_datos_actual": db_actual, "tablas": tables})
