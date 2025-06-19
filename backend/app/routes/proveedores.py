from flask import Blueprint, jsonify
from app.database import mysql

proveedores_bp = Blueprint('proveedores', __name__)

@proveedores_bp.route('/proveedores', methods=['GET'])
def listar_proveedores():
    """
    Listar todos los proveedores activos
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Consulta para obtener todos los proveedores activos
        query = """
            SELECT 
                id,
                nombre,
                contacto,
                telefono,
                email,
                direccion,
                activo,
                fecha_creacion,
                fecha_actualizacion
            FROM proveedores 
            WHERE activo = 1
            ORDER BY nombre
        """
        
        cursor.execute(query)
        proveedores = cursor.fetchall()
        cursor.close()
        
        # Convertir los resultados a formato JSON
        proveedores_list = []
        for proveedor in proveedores:
            proveedores_list.append({
                'id': proveedor[0],
                'nombre': proveedor[1],
                'contacto': proveedor[2],
                'telefono': proveedor[3],
                'email': proveedor[4],
                'direccion': proveedor[5],
                'activo': proveedor[6],
                'fecha_creacion': proveedor[7].strftime('%Y-%m-%d %H:%M:%S') if proveedor[7] else None,
                'fecha_actualizacion': proveedor[8].strftime('%Y-%m-%d %H:%M:%S') if proveedor[8] else None
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
        # Validar que se envió JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'data': None,
                'message': 'El contenido debe ser JSON'
            }), 400
        
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['nombre']
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                return jsonify({
                    'success': False,
                    'data': None,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        cursor = mysql.connection.cursor()
        
        # Verificar si ya existe un proveedor con el mismo nombre
        cursor.execute("SELECT id FROM proveedores WHERE nombre = %s AND activo = 1", (data['nombre'],))
        if cursor.fetchone():
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': 'Ya existe un proveedor con ese nombre'
            }), 400
        
        # Preparar datos para inserción
        nombre = data['nombre']
        contacto = data.get('contacto', '')
        telefono = data.get('telefono', '')
        email = data.get('email', '')
        direccion = data.get('direccion', '')
        
        # Insertar nuevo proveedor
        query = """
            INSERT INTO proveedores (nombre, contacto, telefono, email, direccion, activo, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, 1, NOW())
        """
        
        cursor.execute(query, (nombre, contacto, telefono, email, direccion))
        mysql.connection.commit()
        
        # Obtener el ID del proveedor recién creado
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
        # Validar que se envió JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'data': None,
                'message': 'El contenido debe ser JSON'
            }), 400
        
        data = request.get_json()
        
        # Validar que se enviaron datos para actualizar
        if not data:
            return jsonify({
                'success': False,
                'data': None,
                'message': 'No se enviaron datos para actualizar'
            }), 400
        
        cursor = mysql.connection.cursor()
        
        # Verificar que el proveedor existe
        cursor.execute("SELECT id FROM proveedores WHERE id = %s AND activo = 1", (id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se encontró el proveedor con ID {id}'
            }), 404
        
        # Campos que se pueden actualizar
        campos_permitidos = ['nombre', 'contacto', 'telefono', 'email', 'direccion']
        campos_actualizar = []
        valores = []
        
        for campo in campos_permitidos:
            if campo in data:
                # Validar duplicado de nombre si se está actualizando
                if campo == 'nombre' and data[campo]:
                    cursor.execute("SELECT id FROM proveedores WHERE nombre = %s AND activo = 1 AND id != %s", 
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
        
        # Agregar fecha de actualización
        campos_actualizar.append("fecha_actualizacion = NOW()")
        valores.append(id)  # Para el WHERE
        
        # Construir y ejecutar la consulta
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
    Eliminar un proveedor (soft delete)
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Verificar que el proveedor existe y está activo
        cursor.execute("SELECT nombre FROM proveedores WHERE id = %s AND activo = 1", (id,))
        proveedor = cursor.fetchone()
        
        if not proveedor:
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se encontró el proveedor con ID {id}'
            }), 404
        
        # Verificar si el proveedor tiene productos asociados
        cursor.execute("SELECT COUNT(*) FROM productos WHERE proveedor_id = %s AND activo = 1", (id,))
        productos_count = cursor.fetchone()[0]
        
        if productos_count > 0:
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se puede eliminar el proveedor porque tiene {productos_count} productos asociados'
            }), 400
        
        # Realizar soft delete
        cursor.execute("""
            UPDATE proveedores 
            SET activo = 0, fecha_actualizacion = NOW() 
            WHERE id = %s
        """, (id,))
        
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