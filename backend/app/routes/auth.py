from flask import Blueprint, request, jsonify
from app.database import mysql

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nombre = data.get('nombre')
    password = data.get('password')
    if not nombre or not password:
        return jsonify({'success': False, 'message': 'Nombre y contraseña requeridos'}), 400
    try:
        cursor = mysql.connection.cursor()
        query = '''
            SELECT u.id, u.nombre, u.email, u.contraseña, r.nombre as rol
            FROM usuarios u
            LEFT JOIN roles r ON u.rol_id = r.id
            WHERE u.nombre = %s
        '''
        cursor.execute(query, (nombre,))
        usuario = cursor.fetchone()
        cursor.close()
        if not usuario or usuario[3] != password:
            return jsonify({'success': False, 'message': 'Credenciales incorrectas'}), 401
        usuario_data = {
            'id': usuario[0],
            'nombre': usuario[1],
            'email': usuario[2],
            'rol': usuario[4]
        }
        return jsonify({'success': True, 'usuario': usuario_data}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'}), 500
