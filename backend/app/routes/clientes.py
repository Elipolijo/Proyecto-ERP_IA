from flask import Blueprint, jsonify, request
from app.database import mysql

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes', methods=['GET'])
def listar_clientes():
    """
    Listar todos los clientes
    """
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT 
                id,
                nombre,
                dni,
                telefono,
                email
            FROM clientes 
            ORDER BY nombre
        """
        cursor.execute(query)
        clientes = cursor.fetchall()
        cursor.close()
        clientes_list = []
        for cliente in clientes:
            clientes_list.append({
                'id': cliente[0],
                'nombre': cliente[1],
                'dni': cliente[2],
                'telefono': cliente[3],
                'email': cliente[4]
            })
        return jsonify({
            'success': True,
            'data': clientes_list,
            'message': f'Se encontraron {len(clientes_list)} clientes'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'Error al obtener los clientes: {str(e)}'
        }), 500

@clientes_bp.route('/clientes/<int:id>', methods=['GET'])
def obtener_cliente(id):
    """
    Obtener un cliente específico por ID
    """
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT 
                id,
                nombre,
                dni,
                telefono,
                email
            FROM clientes 
            WHERE id = %s
        """
        cursor.execute(query, (id,))
        cliente = cursor.fetchone()
        cursor.close()
        if not cliente:
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se encontró el cliente con ID {id}'
            }), 404
        cliente_data = {
            'id': cliente[0],
            'nombre': cliente[1],
            'dni': cliente[2],
            'telefono': cliente[3],
            'email': cliente[4]
        }
        return jsonify({
            'success': True,
            'data': cliente_data,
            'message': 'Cliente encontrado exitosamente'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'Error al obtener el cliente: {str(e)}'
        }), 500

@clientes_bp.route('/clientes', methods=['POST'])
def crear_cliente():
    """
    Crear un nuevo cliente
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'data': None,
                'message': 'El contenido debe ser JSON'
            }), 400
        data = request.get_json()
        campos_requeridos = ['nombre', 'dni']
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                return jsonify({
                    'success': False,
                    'data': None,
                    'message': f'El campo {campo} es requerido'
                }), 400
        cursor = mysql.connection.cursor()
        if 'dni' in data and data['dni']:
            cursor.execute("SELECT id FROM clientes WHERE dni = %s", (data['dni'],))
            if cursor.fetchone():
                cursor.close()
                return jsonify({
                    'success': False,
                    'data': None,
                    'message': 'Ya existe un cliente con ese DNI'
                }), 400
        nombre = data['nombre']
        dni = data['dni']
        telefono = data.get('telefono', '')
        email = data.get('email', '')
        query = """
            INSERT INTO clientes (nombre, dni, telefono, email)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, dni, telefono, email))
        mysql.connection.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        return jsonify({
            'success': True,
            'data': {
                'id': nuevo_id,
                'nombre': nombre,
                'dni': dni,
                'telefono': telefono,
                'email': email
            },
            'message': 'Cliente creado exitosamente'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'Error al crear el cliente: {str(e)}'
        }), 500

@clientes_bp.route('/clientes/<int:id>', methods=['PATCH'])
def actualizar_cliente(id):
    """
    Actualizar campos específicos de un cliente
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'data': None,
                'message': 'El contenido debe ser JSON'
            }), 400
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'data': None,
                'message': 'No se enviaron datos para actualizar'
            }), 400
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM clientes WHERE id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se encontró el cliente con ID {id}'
            }), 404
        campos_permitidos = ['nombre', 'dni', 'telefono', 'email']
        campos_actualizar = []
        valores = []
        for campo in campos_permitidos:
            if campo in data:
                if campo == 'dni' and data[campo]:
                    cursor.execute("SELECT id FROM clientes WHERE dni = %s AND id != %s", 
                                 (data[campo], id))
                    if cursor.fetchone():
                        cursor.close()
                        return jsonify({
                            'success': False,
                            'data': None,
                            'message': 'Ya existe otro cliente con ese DNI'
                        }), 400
                campos_actualizar.append(f"{campo} = %s")
                valores.append(data[campo])
        if not campos_actualizar:
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': 'No se especificaron campos válidos para actualizar'
            }), 400
        valores.append(id)
        query = f"UPDATE clientes SET {', '.join(campos_actualizar)} WHERE id = %s"
        cursor.execute(query, valores)
        mysql.connection.commit()
        cursor.close()
        return jsonify({
            'success': True,
            'data': {'id': id, **data},
            'message': 'Cliente actualizado exitosamente'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'Error al actualizar el cliente: {str(e)}'
        }), 500

@clientes_bp.route('/clientes/<int:id>', methods=['DELETE'])
def eliminar_cliente(id):
    """
    Eliminar un cliente (eliminación real)
    """
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT nombre FROM clientes WHERE id = %s", (id,))
        cliente = cursor.fetchone()
        if not cliente:
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se encontró el cliente con ID {id}'
            }), 404
        cursor.execute("SELECT COUNT(*) FROM facturas WHERE cliente_id = %s", (id,))
        facturas_count = cursor.fetchone()[0]
        if facturas_count > 0:
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se puede eliminar el cliente porque tiene {facturas_count} facturas asociadas'
            }), 400
        cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({
            'success': True,
            'data': None,
            'message': f'Cliente "{cliente[0]}" eliminado exitosamente'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'Error al eliminar el cliente: {str(e)}'
        }), 500