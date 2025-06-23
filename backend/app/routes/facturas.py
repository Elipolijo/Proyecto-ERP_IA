from flask import Blueprint, request, jsonify
from app.database import mysql
from datetime import datetime

facturas_bp = Blueprint('facturas', __name__)

@facturas_bp.route('/facturas', methods=['POST'])
def crear_factura():
    """
    CAMINITO COMPLETO: Crear factura con múltiples productos
    Validar → Calcular → Crear factura → Crear detalles → Actualizar stock
    """
    try:
        # 📥 PASO 1: RECIBIR DATOS
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos'
            }), 400
        
        # Validar campos requeridos
        if 'id_cliente' not in data or 'productos' not in data:
            return jsonify({
                'success': False,
                'message': 'Se requieren id_cliente y productos'
            }), 400
        
        id_cliente = data['id_cliente']
        productos = data['productos']
        
        if not productos or len(productos) == 0:
            return jsonify({
                'success': False,
                'message': 'Debe incluir al menos un producto'
            }), 400
        
        cursor = mysql.connection.cursor()
        
        # 🔍 PASO 2: VALIDAR QUE CLIENTE EXISTE
        cursor.execute("SELECT id_cliente, nombre FROM clientes WHERE id_cliente = %s AND activo = 1", 
                      (id_cliente,))
        cliente = cursor.fetchone()
        
        if not cliente:
            cursor.close()
            return jsonify({
                'success': False,
                'message': 'Cliente no encontrado o inactivo'
            }), 404
        
        # 📦 PASO 3: VALIDAR PRODUCTOS Y STOCK
        productos_validados = []
        total_factura = 0
        
        for idx, producto in enumerate(productos):
            # Validar campos del producto
            campos_requeridos = ['id_producto', 'cantidad', 'precio_venta']
            for campo in campos_requeridos:
                if campo not in producto:
                    cursor.close()
                    return jsonify({
                        'success': False,
                        'message': f'Producto {idx + 1}: falta el campo {campo}'
                    }), 400
            
            try:
                id_producto = int(producto['id_producto'])
                cantidad = int(producto['cantidad'])
                precio_venta = float(producto['precio_venta'])
            except (ValueError, TypeError):
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': f'Producto {idx + 1}: tipos de datos inválidos'
                }), 400
            
            if cantidad <= 0:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': f'Producto {idx + 1}: la cantidad debe ser mayor a 0'
                }), 400
            
            if precio_venta <= 0:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': f'Producto {idx + 1}: el precio debe ser mayor a 0'
                }), 400
            
            # Verificar que el producto existe y hay stock suficiente
            cursor.execute("""
                SELECT id_producto, nombre, stock, precio_venta as precio_sugerido
                FROM productos 
                WHERE id_producto = %s AND activo = 1
            """, (id_producto,))
            
            producto_bd = cursor.fetchone()
            
            if not producto_bd:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': f'Producto con ID {id_producto} no encontrado o inactivo'
                }), 404
            
            if producto_bd['stock'] < cantidad:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': f'Stock insuficiente para {producto_bd["nombre"]}. Stock disponible: {producto_bd["stock"]}, solicitado: {cantidad}'
                }), 400
            
            # 💰 CALCULAR SUBTOTAL
            subtotal = cantidad * precio_venta
            total_factura += subtotal
            
            # Guardar producto validado
            productos_validados.append({
                'id_producto': id_producto,
                'nombre': producto_bd['nombre'],
                'cantidad': cantidad,
                'precio_venta': precio_venta,
                'subtotal': subtotal,
                'stock_actual': producto_bd['stock']
            })
        
        # 📝 PASO 4: CREAR FACTURA (tabla facturas)
        query_factura = """
            INSERT INTO facturas (id_cliente, fecha, total, estado, activo)
            VALUES (%s, NOW(), %s, 'pagada', 1)
        """
        
        cursor.execute(query_factura, (id_cliente, total_factura))
        id_factura = cursor.lastrowid
        
        # 📋 PASO 5: CREAR DETALLES (tabla detalle_factura)
        stock_actualizado = []
        
        for producto in productos_validados:
            # Insertar detalle
            query_detalle = """
                INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio_venta, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(query_detalle, (
                id_factura,
                producto['id_producto'],
                producto['cantidad'],
                producto['precio_venta'],
                producto['subtotal']
            ))
            
            # 📦 PASO 6: ACTUALIZAR STOCK
            nuevo_stock = producto['stock_actual'] - producto['cantidad']
            
            cursor.execute("""
                UPDATE productos 
                SET stock = %s 
                WHERE id_producto = %s
            """, (nuevo_stock, producto['id_producto']))
            
             # 📊 NUEVO: REGISTRAR EN DEMANDA_HISTORICA (para IA)
            cursor.execute("""
                INSERT INTO demanda_historica (producto_id, fecha, cantidad_vendida)
                VALUES (%s, NOW(), %s)
            """, (producto['id_producto'], producto['cantidad']))
            
            stock_actualizado.append({
                'producto': producto['nombre'],
                'cantidad_vendida': producto['cantidad'],
                'stock_anterior': producto['stock_actual'],
                'stock_nuevo': nuevo_stock
            })
        
        # 💾 GUARDAR TODO
        mysql.connection.commit()
        cursor.close()
        
        # ✅ PASO 7: RESPONDER
        return jsonify({
            'success': True,
            'message': 'Factura creada exitosamente',
            'data': {
                'id_factura': id_factura,
                'cliente': cliente['nombre'],
                'total': total_factura,
                'productos_vendidos': len(productos_validados),
                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'stock_actualizado': stock_actualizado
            }
        }), 201
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al crear factura: {str(e)}'
        }), 500

@facturas_bp.route('/facturas', methods=['GET'])
def listar_facturas():
    """
    CAMINITO: Consultar BD → Traer facturas con datos de cliente → Responder lista
    """
    try:
        cursor = mysql.connection.cursor()
        
        # 🔍 CONSULTAR FACTURAS CON DATOS DEL CLIENTE
        query = """
            SELECT 
                f.id_factura,
                f.id_cliente,
                c.nombre as nombre_cliente,
                c.email as email_cliente,
                f.fecha,
                f.total,
                f.estado,
                COUNT(df.id_detalle) as cantidad_productos
            FROM facturas f
            JOIN clientes c ON f.id_cliente = c.id_cliente
            LEFT JOIN detalle_factura df ON f.id_factura = df.id_factura
            WHERE f.activo = 1
            GROUP BY f.id_factura
            ORDER BY f.fecha DESC
        """
        
        cursor.execute(query)
        facturas = cursor.fetchall()
        cursor.close()
        
        # 📊 ESTADÍSTICAS ADICIONALES
        total_vendido = sum(factura['total'] for factura in facturas)
        
        return jsonify({
            'success': True,
            'data': facturas,
            'estadisticas': {
                'total_facturas': len(facturas),
                'total_vendido': total_vendido,
                'promedio_por_factura': round(total_vendido / len(facturas), 2) if len(facturas) > 0 else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener facturas: {str(e)}'
        }), 500

@facturas_bp.route('/facturas/<int:id_factura>', methods=['GET'])
def ver_factura(id_factura):
    """
    CAMINITO: Buscar factura → Traer detalles de productos → Responder factura completa
    """
    try:
        cursor = mysql.connection.cursor()
        
        # 🔍 PASO 1: BUSCAR FACTURA CON DATOS DEL CLIENTE
        query_factura = """
            SELECT 
                f.id_factura,
                f.id_cliente,
                c.nombre as nombre_cliente,
                c.email as email_cliente,
                c.telefono as telefono_cliente,
                c.direccion as direccion_cliente,
                f.fecha,
                f.total,
                f.estado
            FROM facturas f
            JOIN clientes c ON f.id_cliente = c.id_cliente
            WHERE f.id_factura = %s AND f.activo = 1
        """
        
        cursor.execute(query_factura, (id_factura,))
        factura = cursor.fetchone()
        
        if not factura:
            cursor.close()
            return jsonify({
                'success': False,
                'message': 'Factura no encontrada'
            }), 404
        
        # 📋 PASO 2: TRAER DETALLES DE PRODUCTOS
        query_detalles = """
            SELECT 
                df.id_detalle,
                df.id_producto,
                p.nombre as nombre_producto,
                p.codigo as codigo_producto,
                df.cantidad,
                df.precio_venta,
                df.subtotal
            FROM detalle_factura df
            JOIN productos p ON df.id_producto = p.id_producto
            WHERE df.id_factura = %s
            ORDER BY df.id_detalle
        """
        
        cursor.execute(query_detalles, (id_factura,))
        detalles = cursor.fetchall()
        cursor.close()
        
        # 📊 CALCULAR ESTADÍSTICAS
        total_productos = sum(detalle['cantidad'] for detalle in detalles)
        
        # ✅ PASO 3: RESPONDER FACTURA COMPLETA
        return jsonify({
            'success': True,
            'data': {
                'factura': factura,
                'detalles': detalles,
                'resumen': {
                    'total_productos': total_productos,
                    'total_lineas': len(detalles),
                    'total_factura': factura['total']
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener factura: {str(e)}'
        }), 500