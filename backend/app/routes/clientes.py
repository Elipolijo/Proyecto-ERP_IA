from flask import Blueprint, jsonify, request
from app.database import mysql

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes', methods=['GET'])
def listar_clientes():
    """
    Listar todos los clientes activos
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Consulta para obtener todos los clientes activos
        query = """
            SELECT 
                id,
                nombre,
                apellido,
                email,
                telefono,
                direccion,
                dni,
                activo,
                fecha_creacion,
                fecha_actualizacion
            FROM clientes 
            WHERE activo = 1
            ORDER BY apellido, nombre
        """
        
        cursor.execute(query)
        clientes = cursor.fetchall()
        cursor.close()
        
        # Convertir los resultados a formato JSON
        clientes_list = []
        for cliente in clientes:
            clientes_list.append({
                'id': cliente[0],
                'nombre': cliente[1],
                'apellido': cliente[2],
                'email': cliente[3],
                'telefono': cliente[4],
                'direccion': cliente[5],
                'dni': cliente[6],
                'activo': cliente[7],
                'fecha_creacion': cliente[8].strftime('%Y-%m-%d %H:%M:%S') if cliente[8] else None,
                'fecha_actualizacion': cliente[9].strftime('%Y-%m-%d %H:%M:%S') if cliente[9] else None
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
        
        # Consulta para obtener un cliente específico
        query = """
            SELECT 
                id,
                nombre,
                apellido,
                email,
                telefono,
                direccion,
                dni,
                activo,
                fecha_creacion,
                fecha_actualizacion
            FROM clientes 
            WHERE id = %s AND activo = 1
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
        
        # Convertir el resultado a formato JSON
        cliente_data = {
            'id': cliente[0],
            'nombre': cliente[1],
            'apellido': cliente[2],
            'email': cliente[3],
            'telefono': cliente[4],
            'direccion': cliente[5],
            'dni': cliente[6],
            'activo': cliente[7],
            'fecha_creacion': cliente[8].strftime('%Y-%m-%d %H:%M:%S') if cliente[8] else None,
            'fecha_actualizacion': cliente[9].strftime('%Y-%m-%d %H:%M:%S') if cliente[9] else None
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
        # Validar que se envió JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'data': None,
                'message': 'El contenido debe ser JSON'
            }), 400
        
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['nombre', 'apellido']
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                return jsonify({
                    'success': False,
                    'data': None,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        cursor = mysql.connection.cursor()
        
        # Verificar si ya existe un cliente con el mismo DNI (si se proporciona)
        if 'dni' in data and data['dni']:
            cursor.execute("SELECT id FROM clientes WHERE dni = %s AND activo = 1", (data['dni'],))
            if cursor.fetchone():
                cursor.close()
                return jsonify({
                    'success': False,
                    'data': None,
                    'message': 'Ya existe un cliente con ese DNI'
                }), 400
        
        # Preparar datos para inserción
        nombre = data['nombre']
        apellido = data['apellido']
        email = data.get('email', '')
        telefono = data.get('telefono', '')
        direccion = data.get('direccion', '')
        dni = data.get('dni', '')
        
        # Insertar nuevo cliente
        query = """
            INSERT INTO clientes (nombre, apellido, email, telefono, direccion, dni, activo, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, 1, NOW())
        """
        
        cursor.execute(query, (nombre, apellido, email, telefono, direccion, dni))
        mysql.connection.commit()
        
        # Obtener el ID del cliente recién creado
        nuevo_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({
            'success': True,
            'data': {
                'id': nuevo_id,
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'telefono': telefono,
                'direccion': direccion,
                'dni': dni
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
        
        # Verificar que el cliente existe
        cursor.execute("SELECT id FROM clientes WHERE id = %s AND activo = 1", (id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se encontró el cliente con ID {id}'
            }), 404
        
        # Campos que se pueden actualizar
        campos_permitidos = ['nombre', 'apellido', 'email', 'telefono', 'direccion', 'dni']
        campos_actualizar = []
        valores = []
        
        for campo in campos_permitidos:
            if campo in data:
                # Validar duplicado de DNI si se está actualizando
                if campo == 'dni' and data[campo]:
                    cursor.execute("SELECT id FROM clientes WHERE dni = %s AND activo = 1 AND id != %s", 
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
        
        # Agregar fecha de actualización
        campos_actualizar.append("fecha_actualizacion = NOW()")
        valores.append(id)  # Para el WHERE
        
        # Construir y ejecutar la consulta
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
    Eliminar un cliente (soft delete)
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Verificar que el cliente existe y está activo
        cursor.execute("SELECT nombre, apellido FROM clientes WHERE id = %s AND activo = 1", (id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se encontró el cliente con ID {id}'
            }), 404
        
        # Verificar si el cliente tiene facturas asociadas
        cursor.execute("SELECT COUNT(*) FROM facturas WHERE cliente_id = %s", (id,))
        facturas_count = cursor.fetchone()[0]
        
        if facturas_count > 0:
            cursor.close()
            return jsonify({
                'success': False,
                'data': None,
                'message': f'No se puede eliminar el cliente porque tiene {facturas_count} facturas asociadas'
            }), 400
        
        # Realizar soft delete
        cursor.execute("""
            UPDATE clientes 
            SET activo = 0, fecha_actualizacion = NOW() 
            WHERE id = %s
        """, (id,))
        
        mysql.connection.commit()
        cursor.close()
        
        nombre_completo = f"{cliente[0]} {cliente[1]}"
        
        return jsonify({
            'success': True,
            'data': None,
            'message': f'Cliente "{nombre_completo}" eliminado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'data': None,
            'message': f'Error al eliminar el cliente: {str(e)}'
        }), 500