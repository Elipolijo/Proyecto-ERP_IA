from flask import Blueprint, request, jsonify
from ..database import mysql

categorias_bp = Blueprint('categorias', __name__)

# Acá van a ir las rutas
@categorias_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    """Listar todas las categorías activas"""
    try:
        cursor = mysql.connection.cursor()
        query = """
        SELECT id, nombre, descripcion, activo, fecha_creacion, fecha_actualizacion
        FROM categorias 
        WHERE activo = 1
        ORDER BY nombre
        """
        cursor.execute(query)
        categorias = cursor.fetchall()
        cursor.close()
        
        # Convertir a diccionario
        categorias_list = []
        for categoria in categorias:
            categorias_list.append({
                'id': categoria[0],
                'nombre': categoria[1],
                'descripcion': categoria[2],
                'activo': bool(categoria[3]),
                'fecha_creacion': categoria[4].isoformat() if categoria[4] else None,
                'fecha_actualizacion': categoria[5].isoformat() if categoria[5] else None
            })
        
        return jsonify({
            'success': True,
            'data': categorias_list,
            'total': len(categorias_list)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
 @categorias_bp.route('/categorias/<int:categoria_id>', methods=['GET'])
def obtener_categoria(categoria_id):
    """Obtener una categoría específica por ID"""
    try:
        cursor = mysql.connection.cursor()
        query = """
        SELECT id, nombre, descripcion, activo, fecha_creacion, fecha_actualizacion
        FROM categorias 
        WHERE id = %s AND activo = 1
        """
        cursor.execute(query, (categoria_id,))
        categoria = cursor.fetchone()
        cursor.close()
        
        if not categoria:
            return jsonify({
                'success': False, 
                'error': 'Categoría no encontrada'
            }), 404
        
        categoria_data = {
            'id': categoria[0],
            'nombre': categoria[1],
            'descripcion': categoria[2],
            'activo': bool(categoria[3]),
            'fecha_creacion': categoria[4].isoformat() if categoria[4] else None,
            'fecha_actualizacion': categoria[5].isoformat() if categoria[5] else None
        }
        
        return jsonify({
            'success': True,
            'data': categoria_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500   
    
@categorias_bp.route('/categorias', methods=['POST'])
def crear_categoria():
    """Crear una nueva categoría"""
    try:
        data = request.json
        
        # Validar campos requeridos
        if not data or 'nombre' not in data or not data['nombre'].strip():
            return jsonify({
                'success': False,
                'error': 'El nombre de la categoría es requerido'
            }), 400
        
        cursor = mysql.connection.cursor()
        
        # Verificar que no exista una categoría con el mismo nombre
        cursor.execute(
            "SELECT id FROM categorias WHERE nombre = %s AND activo = 1", 
            (data['nombre'].strip(),)
        )
        if cursor.fetchone():
            cursor.close()
            return jsonify({
                'success': False,
                'error': 'Ya existe una categoría con ese nombre'
            }), 400
        
        # Insertar nueva categoría
        query = """
        INSERT INTO categorias (nombre, descripcion, activo)
        VALUES (%s, %s, %s)
        """
        valores = (
            data['nombre'].strip(),
            data.get('descripcion', '').strip(),
            True
        )
        
        cursor.execute(query, valores)
        categoria_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'data': {'id': categoria_id},
            'message': 'Categoría creada exitosamente'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 
    
@categorias_bp.route('/categorias/<int:categoria_id>', methods=['PATCH'])
def actualizar_categoria_parcial(categoria_id):
    """Actualizar campos específicos de una categoría"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No hay datos para actualizar'
            }), 400
        
        cursor = mysql.connection.cursor()
        
        # Verificar que la categoría existe
        cursor.execute("SELECT id FROM categorias WHERE id = %s AND activo = 1", (categoria_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({
                'success': False, 
                'error': 'Categoría no encontrada'
            }), 404
        
        # Verificar nombre duplicado si se está actualizando el nombre
        if 'nombre' in data and data['nombre'].strip():
            cursor.execute(
                "SELECT id FROM categorias WHERE nombre = %s AND id != %s AND activo = 1", 
                (data['nombre'].strip(), categoria_id)
            )
            if cursor.fetchone():
                cursor.close()
                return jsonify({
                    'success': False,
                    'error': 'Ya existe una categoría con ese nombre'
                }), 400
        
        # Construir query dinámicamente
        campos_actualizar = []
        valores = []
        
        campos_permitidos = ['nombre', 'descripcion']
        
        for campo in campos_permitidos:
            if campo in data:
                if campo == 'nombre' and not data[campo].strip():
                    cursor.close()
                    return jsonify({
                        'success': False,
                        'error': 'El nombre no puede estar vacío'
                    }), 400
                
                campos_actualizar.append(f"{campo} = %s")
                valores.append(data[campo].strip() if isinstance(data[campo], str) else data[campo])
        
        if not campos_actualizar:
            cursor.close()
            return jsonify({
                'success': False,
                'error': 'No hay campos válidos para actualizar'
            }), 400
        
        # Agregar fecha de actualización
        campos_actualizar.append("fecha_actualizacion = NOW()")
        valores.append(categoria_id)
        
        query = f"UPDATE categorias SET {', '.join(campos_actualizar)} WHERE id = %s"
        cursor.execute(query, valores)
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Categoría actualizada exitosamente'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500       
    
@categorias_bp.route('/categorias/<int:categoria_id>', methods=['DELETE'])
def eliminar_categoria(categoria_id):
    """Eliminar una categoría (soft delete)"""
    try:
        cursor = mysql.connection.cursor()
        
        # Verificar que la categoría existe
        cursor.execute("SELECT id FROM categorias WHERE id = %s AND activo = 1", (categoria_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({
                'success': False, 
                'error': 'Categoría no encontrada'
            }), 404
        
        # Verificar si hay productos asociados a esta categoría
        cursor.execute(
            "SELECT COUNT(*) FROM productos WHERE categoria_id = %s AND activo = 1", 
            (categoria_id,)
        )
        productos_count = cursor.fetchone()[0]
        
        if productos_count > 0:
            cursor.close()
            return jsonify({
                'success': False,
                'error': f'No se puede eliminar la categoría porque tiene {productos_count} producto(s) asociado(s)'
            }), 400
        
        # Soft delete - marcar como inactiva
        cursor.execute(
            "UPDATE categorias SET activo = 0, fecha_actualizacion = NOW() WHERE id = %s",
            (categoria_id,)
        )
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Categoría eliminada exitosamente'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500    