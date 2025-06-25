from flask import Blueprint, jsonify, request
from app.database import mysql

proveedores_bp = Blueprint('proveedores', __name__)

@proveedores_bp.route('/proveedores', methods=['GET'])
def listar_proveedores():
    """
    Listar todos los proveedores
    """
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT 
                id,
                nombre,
                contacto,
                telefono,
                email,
                direccion
            FROM proveedores 
            ORDER BY nombre
        """
        cursor.execute(query)
        proveedores = cursor.fetchall()
        cursor.close()
        proveedores_list = []
        for proveedor in proveedores:
            proveedores_list.append({
                'id': proveedor[0],
                'nombre': proveedor[1],
                'contacto': proveedor[2],
                'telefono': proveedor[3],
                'email': proveedor[4],
                'direccion': proveedor[5]
            })
        return jsonify({
            'success': True,
            'data': proveedores_list,
            'message': f'Se encontraron {len(proveedores_list)} proveedores'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'Error al obtener los proveedores: {str(e)}'
        }), 500

@proveedores_bp.route('/proveedores', methods=['POST'])
def crear_proveedor():
    """
    Crear un nuevo proveedor
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'data': None,
                'message': 'El contenido debe ser JSON'
            }), 400
        data = request.get_json()
        campos_requeridos = ['nombre']
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                return jsonify({
                    'success': False,
                    'data': None,
                    'message': f'El campo {campo} es requerido'
                }), 400
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM proveedores WHERE nombre = %s", (data['nombre'],))
        if cursor.fetchone():
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': 'Ya existe un proveedor con ese nombre'
            }), 400
        nombre = data['nombre']
        contacto = data.get('contacto', '')
        telefono = data.get('telefono', '')
        email = data.get('email', '')
        direccion = data.get('direccion', '')
        query = """
            INSERT INTO proveedores (nombre, contacto, telefono, email, direccion)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, contacto, telefono, email, direccion))
        mysql.connection.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        return jsonify({
            'success': True,
            'data': {
                'id': nuevo_id,
                'nombre': nombre,
                'contacto': contacto,
                'telefono': telefono,
                'email': email,
                'direccion': direccion
            },
            'message': 'Proveedor creado exitosamente'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'Error al crear el proveedor: {str(e)}'
        }), 500

@proveedores_bp.route('/proveedores/<int:id>', methods=['PATCH'])
def actualizar_proveedor(id):
    """
    Actualizar campos específicos de un proveedor
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
        cursor.execute("SELECT id FROM proveedores WHERE id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se encontró el proveedor con ID {id}'
            }), 404
        campos_permitidos = ['nombre', 'contacto', 'telefono', 'email', 'direccion']
        campos_actualizar = []
        valores = []
        for campo in campos_permitidos:
            if campo in data:
                if campo == 'nombre' and data[campo]:
                    cursor.execute("SELECT id FROM proveedores WHERE nombre = %s AND id != %s", 
                                 (data[campo], id))
                    if cursor.fetchone():
                        cursor.close()
                        return jsonify({
                            'success': False,
                            'data': None,
                            'message': 'Ya existe otro proveedor con ese nombre'
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
        query = f"UPDATE proveedores SET {', '.join(campos_actualizar)} WHERE id = %s"
        cursor.execute(query, valores)
        mysql.connection.commit()
        cursor.close()
        return jsonify({
            'success': True,
            'data': {'id': id, **data},
            'message': 'Proveedor actualizado exitosamente'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'Error al actualizar el proveedor: {str(e)}'
        }), 500

@proveedores_bp.route('/proveedores/<int:id>', methods=['DELETE'])
def eliminar_proveedor(id):
    """
    Eliminar un proveedor (eliminación real)
    """
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT nombre FROM proveedores WHERE id = %s", (id,))
        proveedor = cursor.fetchone()
        if not proveedor:
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se encontró el proveedor con ID {id}'
            }), 404
        # Verificar si el proveedor tiene productos asociados
        cursor.execute("SELECT COUNT(*) FROM productos WHERE proveedor_id = %s", (id,))
        productos_count = cursor.fetchone()[0]
        if productos_count > 0:
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se puede eliminar el proveedor porque tiene {productos_count} productos asociados'
            }), 400
        cursor.execute("DELETE FROM proveedores WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({
            'success': True,
            'data': None,
            'message': f'Proveedor "{proveedor[0]}" eliminado exitosamente'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'Error al eliminar el proveedor: {str(e)}'
        }), 500