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
        if 'cliente_id' not in data or 'productos' not in data:
            return jsonify({
                'success': False,
                'message': 'Se requieren cliente_id y productos'
            }), 400
        
        cliente_id = data['cliente_id']
        productos = data['productos']
        
        if not productos or len(productos) == 0:
            return jsonify({
                'success': False,
                'message': 'Debe incluir al menos un producto'
            }), 400
        
        cursor = mysql.connection.cursor()
        
        # 🔍 PASO 2: VALIDAR QUE CLIENTE EXISTE
        cursor.execute("SELECT id, nombre FROM clientes WHERE id = %s", 
                      (cliente_id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            cursor.close()
            return jsonify({
                'success': False,
                'message': 'Cliente no encontrado'
            }), 404
        
        # 📦 PASO 3: VALIDAR PRODUCTOS Y STOCK
        productos_validados = []
        total_factura = 0
        
        for idx, producto in enumerate(productos):
            # Validar campos del producto
            campos_requeridos = ['producto_id', 'cantidad', 'precio_unitario']
            for campo in campos_requeridos:
                if campo not in producto:
                    cursor.close()
                    return jsonify({
                        'success': False,
                        'message': f'Producto {idx + 1}: falta el campo {campo}'
                    }), 400
            
            try:
                producto_id = int(producto['producto_id'])
                cantidad = int(producto['cantidad'])
                precio_unitario = float(producto['precio_unitario'])
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
            
            if precio_unitario <= 0:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': f'Producto {idx + 1}: el precio debe ser mayor a 0'
                }), 400
            
            # Verificar que el producto existe y hay stock suficiente
            cursor.execute("SELECT id, nombre, stock_actual FROM productos WHERE id = %s", (producto_id,))
            
            producto_bd = cursor.fetchone()
            
            if not producto_bd:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': f'Producto con ID {producto_id} no encontrado'
                }), 404
            
            if producto_bd[2] < cantidad:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': f'Stock insuficiente para {producto_bd[1]}. Stock disponible: {producto_bd[2]}, solicitado: {cantidad}'
                }), 400
            
            # 💰 CALCULAR SUBTOTAL
            subtotal = cantidad * precio_unitario
            total_factura += subtotal
            
            # Guardar producto validado
            productos_validados.append({
                'producto_id': producto_id,
                'nombre': producto_bd[1],
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'subtotal': subtotal,
                'stock_actual': producto_bd[2]
            })
        
        # 📝 PASO 4: CREAR FACTURA (tabla facturas)
        query_factura = """
            INSERT INTO facturas (cliente_id, fecha, total)
            VALUES (%s, NOW(), %s)
        """
        
        cursor.execute(query_factura, (cliente_id, total_factura))
        factura_id = cursor.lastrowid
        
        # 📋 PASO 5: CREAR DETALLES (tabla detalle_factura)
        stock_actualizado = []
        
        for producto in productos_validados:
            # Insertar detalle
            query_detalle = """
                INSERT INTO detalle_factura (factura_id, producto_id, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(query_detalle, (
                factura_id,
                producto['producto_id'],
                producto['cantidad'],
                producto['precio_unitario']
            ))
            
            # 📦 PASO 6: ACTUALIZAR STOCK
            nuevo_stock = producto['stock_actual'] - producto['cantidad']
            
            cursor.execute("UPDATE productos SET stock_actual = %s WHERE id = %s", (nuevo_stock, producto['producto_id']))
            
             # 📊 NUEVO: REGISTRAR EN DEMANDA_HISTORICA (para IA)
            cursor.execute("INSERT INTO demanda_historica (producto_id, fecha, cantidad_vendida) VALUES (%s, NOW(), %s)", (producto['producto_id'], producto['cantidad']))
            
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
                'factura_id': factura_id,
                'cliente': cliente[1],
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
                f.id,
                f.cliente_id,
                c.nombre as nombre_cliente,
                c.email as email_cliente,
                f.fecha,
                f.total
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            ORDER BY f.fecha DESC
        """
        
        cursor.execute(query)
        facturas = cursor.fetchall()
        cursor.close()
        
        # 📊 ESTADÍSTICAS ADICIONALES
        total_vendido = sum(factura[5] for factura in facturas)
        
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

@facturas_bp.route('/facturas/<int:factura_id>', methods=['GET'])
def ver_factura(factura_id):
    """
    CAMINITO: Buscar factura → Traer detalles de productos → Responder factura completa
    """
    try:
        cursor = mysql.connection.cursor()
        
        # 🔍 PASO 1: BUSCAR FACTURA CON DATOS DEL CLIENTE
        query_factura = """
            SELECT 
                f.id,
                f.cliente_id,
                c.nombre as nombre_cliente,
                c.email as email_cliente,
                c.telefono as telefono_cliente,
                f.fecha,
                f.total
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            WHERE f.id = %s
        """
        
        cursor.execute(query_factura, (factura_id,))
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
                df.id,
                df.producto_id,
                p.nombre as nombre_producto,
                df.cantidad,
                df.precio_unitario
            FROM detalle_factura df
            JOIN productos p ON df.producto_id = p.id
            WHERE df.factura_id = %s
            ORDER BY df.id
        """
        
        cursor.execute(query_detalles, (factura_id,))
        detalles = cursor.fetchall()
        cursor.close()
        
        # 📊 CALCULAR ESTADÍSTICAS
        total_productos = sum(detalle[3] for detalle in detalles)
        
        # ✅ PASO 3: RESPONDER FACTURA COMPLETA
        return jsonify({
            'success': True,
            'data': {
                'factura': factura,
                'detalles': detalles,
                'resumen': {
                    'total_productos': total_productos,
                    'total_lineas': len(detalles),
                    'total_factura': factura[6]
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener factura: {str(e)}'
        }), 500