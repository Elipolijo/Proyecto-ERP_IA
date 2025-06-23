from flask import Blueprint, request, jsonify
from app.database import mysql
from datetime import datetime

entrada_stock_bp = Blueprint('entrada_stock', __name__)

@entrada_stock_bp.route('/entradas-stock', methods=['GET'])
def listar_entradas():
    """Listar todas las entradas de stock con información de productos y proveedores"""
    try:
        cursor = mysql.connection.cursor()
        
        # Query con JOINs para obtener nombres de producto y proveedor
        query = """
            SELECT 
                es.id_entrada,
                es.id_producto,
                p.nombre as nombre_producto,
                p.codigo as codigo_producto,
                es.id_proveedor,
                pr.nombre as nombre_proveedor,
                es.cantidad,
                es.precio_compra,
                es.fecha_entrada,
                es.activo
            FROM entrada_stock es
            JOIN productos p ON es.id_producto = p.id_producto
            JOIN proveedores pr ON es.id_proveedor = pr.id_proveedor
            WHERE es.activo = 1
            ORDER BY es.fecha_entrada DESC
        """
        
        cursor.execute(query)
        entradas = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'data': entradas,
            'total': len(entradas)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener entradas de stock: {str(e)}'
        }), 500

@entrada_stock_bp.route('/entradas-stock/<int:id_entrada>', methods=['GET'])
def obtener_entrada(id_entrada):
    """Obtener una entrada de stock específica"""
    try:
        cursor = mysql.connection.cursor()
        
        query = """
            SELECT 
                es.id_entrada,
                es.id_producto,
                p.nombre as nombre_producto,
                p.codigo as codigo_producto,
                es.id_proveedor,
                pr.nombre as nombre_proveedor,
                es.cantidad,
                es.precio_compra,
                es.fecha_entrada,
                es.activo
            FROM entrada_stock es
            JOIN productos p ON es.id_producto = p.id_producto
            JOIN proveedores pr ON es.id_proveedor = pr.id_proveedor
            WHERE es.id_entrada = %s AND es.activo = 1
        """
        
        cursor.execute(query, (id_entrada,))
        entrada = cursor.fetchone()
        cursor.close()
        
        if not entrada:
            return jsonify({
                'success': False,
                'message': 'Entrada de stock no encontrada'
            }), 404
            
        return jsonify({
            'success': True,
            'data': entrada
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener entrada de stock: {str(e)}'
        }), 500

@entrada_stock_bp.route('/entradas-stock', methods=['POST'])
def crear_entrada():
    """Crear nueva entrada de stock y actualizar stock del producto"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['id_producto', 'id_proveedor', 'cantidad', 'precio_compra']
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None:
                return jsonify({
                    'success': False,
                    'message': f'El campo {campo} es requerido'
                }), 400
        
        # Validar tipos y valores
        try:
            cantidad = int(data['cantidad'])
            precio_compra = float(data['precio_compra'])
            id_producto = int(data['id_producto'])
            id_proveedor = int(data['id_proveedor'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Tipos de datos inválidos'
            }), 400
        
        if cantidad <= 0:
            return jsonify({
                'success': False,
                'message': 'La cantidad debe ser mayor a 0'
            }), 400
            
        if precio_compra < 0:
            return jsonify({
                'success': False,
                'message': 'El precio de compra no puede ser negativo'
            }), 400
        
        cursor = mysql.connection.cursor()
        
        # Verificar que el producto existe y está activo
        cursor.execute("SELECT id_producto, stock FROM productos WHERE id_producto = %s AND activo = 1", 
                      (id_producto,))
        producto = cursor.fetchone()
        
        if not producto:
            cursor.close()
            return jsonify({
                'success': False,
                'message': 'Producto no encontrado o inactivo'
            }), 404
        
        # Verificar que el proveedor existe y está activo
        cursor.execute("SELECT id_proveedor FROM proveedores WHERE id_proveedor = %s AND activo = 1", 
                      (id_proveedor,))
        proveedor = cursor.fetchone()
        
        if not proveedor:
            cursor.close()
            return jsonify({
                'success': False,
                'message': 'Proveedor no encontrado o inactivo'
            }), 404
        
        # Insertar nueva entrada de stock
        query_entrada = """
            INSERT INTO entrada_stock (id_producto, id_proveedor, cantidad, precio_compra, fecha_entrada, activo)
            VALUES (%s, %s, %s, %s, NOW(), 1)
        """
        
        cursor.execute(query_entrada, (id_producto, id_proveedor, cantidad, precio_compra))
        id_nueva_entrada = cursor.lastrowid
        
        # Actualizar stock del producto
        nuevo_stock = producto['stock'] + cantidad
        cursor.execute("UPDATE productos SET stock = %s WHERE id_producto = %s", 
                      (nuevo_stock, id_producto))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Entrada de stock registrada exitosamente',
            'data': {
                'id_entrada': id_nueva_entrada,
                'stock_anterior': producto['stock'],
                'stock_nuevo': nuevo_stock,
                'cantidad_agregada': cantidad
            }
        }), 201
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al crear entrada de stock: {str(e)}'
        }), 500

@entrada_stock_bp.route('/entradas-stock/<int:id_entrada>', methods=['PATCH'])
def modificar_entrada(id_entrada):
    """Modificar entrada de stock existente y recalcular stock del producto"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos para actualizar'
            }), 400
        
        cursor = mysql.connection.cursor()
        
        # Obtener entrada actual
        query_entrada = """
            SELECT es.id_entrada, es.id_producto, es.cantidad, es.precio_compra, es.activo,
                   p.stock as stock_actual
            FROM entrada_stock es
            JOIN productos p ON es.id_producto = p.id_producto
            WHERE es.id_entrada = %s AND es.activo = 1
        """
        
        cursor.execute(query_entrada, (id_entrada,))
        entrada_actual = cursor.fetchone()
        
        if not entrada_actual:
            cursor.close()
            return jsonify({
                'success': False,
                'message': 'Entrada de stock no encontrada'
            }), 404
        
        # Preparar campos a actualizar
        campos_actualizar = []
        valores = []
        
        cantidad_nueva = entrada_actual['cantidad']  # Por defecto mantener la actual
        
        # Validar y preparar campos
        if 'cantidad' in data:
            try:
                cantidad_nueva = int(data['cantidad'])
                if cantidad_nueva <= 0:
                    raise ValueError("La cantidad debe ser mayor a 0")
                campos_actualizar.append("cantidad = %s")
                valores.append(cantidad_nueva)
            except (ValueError, TypeError) as e:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': f'Cantidad inválida: {str(e)}'
                }), 400
        
        if 'precio_compra' in data:
            try:
                precio_compra = float(data['precio_compra'])
                if precio_compra < 0:
                    raise ValueError("El precio no puede ser negativo")
                campos_actualizar.append("precio_compra = %s")
                valores.append(precio_compra)
            except (ValueError, TypeError) as e:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': f'Precio inválido: {str(e)}'
                }), 400
        
        if not campos_actualizar:
            cursor.close()
            return jsonify({
                'success': False,
                'message': 'No hay campos válidos para actualizar'
            }), 400
        
        # Recalcular stock si cambió la cantidad
        diferencia_cantidad = cantidad_nueva - entrada_actual['cantidad']
        nuevo_stock = entrada_actual['stock_actual'] + diferencia_cantidad
        
        if nuevo_stock < 0:
            cursor.close()
            return jsonify({
                'success': False,
                'message': 'La modificación resultaría en stock negativo'
            }), 400
        
        # Actualizar entrada de stock
        query_update = f"UPDATE entrada_stock SET {', '.join(campos_actualizar)} WHERE id_entrada = %s"
        valores.append(id_entrada)
        cursor.execute(query_update, valores)
        
        # Actualizar stock del producto si cambió la cantidad
        if diferencia_cantidad != 0:
            cursor.execute("UPDATE productos SET stock = %s WHERE id_producto = %s", 
                          (nuevo_stock, entrada_actual['id_producto']))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Entrada de stock actualizada exitosamente',
            'data': {
                'cantidad_anterior': entrada_actual['cantidad'],
                'cantidad_nueva': cantidad_nueva,
                'diferencia': diferencia_cantidad,
                'stock_nuevo': nuevo_stock
            }
        }), 200
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al modificar entrada de stock: {str(e)}'
        }), 500

@entrada_stock_bp.route('/entradas-stock/<int:id_entrada>', methods=['DELETE'])
def anular_entrada(id_entrada):
    """Anular entrada de stock (soft delete) y ajustar stock del producto"""
    try:
        cursor = mysql.connection.cursor()
        
        # Obtener entrada actual
        query_entrada = """
            SELECT es.id_entrada, es.id_producto, es.cantidad, es.activo,
                   p.stock as stock_actual, p.nombre as nombre_producto
            FROM entrada_stock es
            JOIN productos p ON es.id_producto = p.id_producto
            WHERE es.id_entrada = %s AND es.activo = 1
        """
        
        cursor.execute(query_entrada, (id_entrada,))
        entrada = cursor.fetchone()
        
        if not entrada:
            cursor.close()
            return jsonify({
                'success': False,
                'message': 'Entrada de stock no encontrada o ya anulada'
            }), 404
        
        # Verificar que hay suficiente stock para restar
        if entrada['stock_actual'] < entrada['cantidad']:
            cursor.close()
            return jsonify({
                'success': False,
                'message': f'No se puede anular: stock insuficiente. Stock actual: {entrada["stock_actual"]}, cantidad a restar: {entrada["cantidad"]}'
            }), 400
        
        # Calcular nuevo stock
        nuevo_stock = entrada['stock_actual'] - entrada['cantidad']
        
        # Anular entrada (soft delete)
        cursor.execute("UPDATE entrada_stock SET activo = 0 WHERE id_entrada = %s", (id_entrada,))
        
        # Actualizar stock del producto
        cursor.execute("UPDATE productos SET stock = %s WHERE id_producto = %s", 
                      (nuevo_stock, entrada['id_producto']))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Entrada de stock anulada exitosamente',
            'data': {
                'producto': entrada['nombre_producto'],
                'cantidad_restada': entrada['cantidad'],
                'stock_anterior': entrada['stock_actual'],
                'stock_nuevo': nuevo_stock,
                'nota': 'La entrada se mantiene en el historial para análisis de demanda'
            }
        }), 200
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al anular entrada de stock: {str(e)}'
        }), 500

@entrada_stock_bp.route('/entradas-stock/producto/<int:id_producto>', methods=['GET'])
def entradas_por_producto(id_producto):
    """Obtener todas las entradas de stock de un producto específico"""
    try:
        cursor = mysql.connection.cursor()
        
        query = """
            SELECT 
                es.id_entrada,
                es.cantidad,
                es.precio_compra,
                es.fecha_entrada,
                es.activo,
                pr.nombre as nombre_proveedor
            FROM entrada_stock es
            JOIN proveedores pr ON es.id_proveedor = pr.id_proveedor
            WHERE es.id_producto = %s
            ORDER BY es.fecha_entrada DESC
        """
        
        cursor.execute(query, (id_producto,))
        entradas = cursor.fetchall()
        cursor.close()
        
        return jsonify({
            'success': True,
            'data': entradas,
            'total': len(entradas)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener entradas del producto: {str(e)}'
        }), 500