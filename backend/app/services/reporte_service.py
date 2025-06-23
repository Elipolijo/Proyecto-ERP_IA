"""
Servicio de Reportes de IA
Conecta la base de datos con los algoritmos de IA para generar reportes inteligentes
"""

from app.database import mysql
from app.ia.algoritmos import (
    calcular_promedio_movil,
    calcular_dias_hasta_agotamiento,
    detectar_sobrestock,
    calcular_rotacion_producto,
    identificar_stock_critico,
    predecir_demanda_futura
)
from datetime import datetime, timedelta

class ReporteService:
    
    @staticmethod
    def obtener_reporte_stock_critico():
        """
        Genera reporte de productos con stock crítico
        """
        try:
            cursor = mysql.connection.cursor()
            
            # Consulta productos con información completa
            query = """
            SELECT 
                p.id, p.nombre, p.stock_actual, p.stock_minimo,
                p.precio_venta, c.nombre as categoria_nombre,
                pr.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            WHERE p.activo = 1
            ORDER BY (p.stock_actual / NULLIF(p.stock_minimo, 0)) ASC
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            cursor.close()
            
            productos_criticos = []
            
            for producto in productos:
                # Usar algoritmo de IA para evaluar criticidad
                analisis = identificar_stock_critico(
                    producto['stock_actual'], 
                    producto['stock_minimo']
                )
                
                if analisis['es_critico']:
                    productos_criticos.append({
                        'id': producto['id'],
                        'nombre': producto['nombre'],
                        'stock_actual': producto['stock_actual'],
                        'stock_minimo': producto['stock_minimo'],
                        'precio_venta': float(producto['precio_venta']),
                        'categoria': producto['categoria_nombre'],
                        'proveedor': producto['proveedor_nombre'],
                        'nivel_alerta': analisis['nivel_alerta'],
                        'accion_sugerida': analisis['accion_sugerida']
                    })
            
            return {
                'success': True,
                'data': productos_criticos,
                'total_criticos': len(productos_criticos),
                'fecha_reporte': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al generar reporte de stock crítico: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def obtener_reporte_prediccion_demanda():
        """
        Genera reporte de predicción de demanda basado en historial de ventas
        """
        try:
            cursor = mysql.connection.cursor()
            
            # Obtener productos con sus ventas históricas
            query = """
            SELECT 
                p.id, p.nombre, p.stock_actual,
                c.nombre as categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.activo = 1
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            predicciones = []
            
            for producto in productos:
                # Obtener historial de ventas del producto
                ventas_query = """
                SELECT 
                    DATE(f.fecha_factura) as fecha,
                    SUM(df.cantidad) as cantidad
                FROM detalle_factura df
                JOIN facturas f ON df.factura_id = f.id
                WHERE df.producto_id = %s
                    AND f.fecha_factura >= DATE_SUB(NOW(), INTERVAL 90 DAY)
                GROUP BY DATE(f.fecha_factura)
                ORDER BY fecha
                """
                
                cursor.execute(ventas_query, (producto['id'],))
                ventas_historial = cursor.fetchall()
                
                if ventas_historial:
                    # Convertir a formato para algoritmos IA
                    ventas_data = [
                        {
                            'fecha': venta['fecha'].strftime('%Y-%m-%d'),
                            'cantidad': int(venta['cantidad'])
                        }
                        for venta in ventas_historial
                    ]
                    
                    # Calcular promedio móvil y predicción
                    promedio_diario = calcular_promedio_movil(ventas_data, 30)
                    prediccion = predecir_demanda_futura(ventas_data, 30)
                    
                    predicciones.append({
                        'id': producto['id'],
                        'nombre': producto['nombre'],
                        'stock_actual': producto['stock_actual'],
                        'categoria': producto['categoria_nombre'],
                        'promedio_ventas_diarias': round(promedio_diario, 2),
                        'demanda_estimada_30_dias': prediccion['demanda_estimada'],
                        'tendencia': prediccion['tendencia'],
                        'confianza': prediccion['confianza'],
                        'stock_sugerido': max(
                            producto['stock_actual'], 
                            int(prediccion['demanda_estimada'] * 1.2)  # 20% buffer
                        )
                    })
            
            cursor.close()
            
            return {
                'success': True,
                'data': predicciones,
                'total_productos': len(predicciones),
                'fecha_reporte': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al generar predicción de demanda: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def obtener_reporte_prediccion_agotamiento():
        """
        Predice cuándo se agotará cada producto
        """
        try:
            cursor = mysql.connection.cursor()
            
            # Obtener productos con ventas recientes
            query = """
            SELECT 
                p.id, p.nombre, p.stock_actual, p.stock_minimo,
                c.nombre as categoria_nombre,
                pr.nombre as proveedor_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            WHERE p.activo = 1 AND p.stock_actual > 0
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            predicciones_agotamiento = []
            
            for producto in productos:
                # Obtener ventas últimos 30 días
                ventas_query = """
                SELECT 
                    DATE(f.fecha_factura) as fecha,
                    SUM(df.cantidad) as cantidad
                FROM detalle_factura df
                JOIN facturas f ON df.factura_id = f.id
                WHERE df.producto_id = %s
                    AND f.fecha_factura >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY DATE(f.fecha_factura)
                """
                
                cursor.execute(ventas_query, (producto['id'],))
                ventas_recientes = cursor.fetchall()
                
                if ventas_recientes:
                    # Calcular promedio de ventas diarias
                    ventas_data = [
                        {
                            'fecha': venta['fecha'].strftime('%Y-%m-%d'),
                            'cantidad': int(venta['cantidad'])
                        }
                        for venta in ventas_recientes
                    ]
                    
                    promedio_diario = calcular_promedio_movil(ventas_data, 30)
                    dias_agotamiento = calcular_dias_hasta_agotamiento(
                        producto['stock_actual'], 
                        promedio_diario
                    )
                    
                    # Calcular fecha estimada de agotamiento
                    if dias_agotamiento < 999:
                        fecha_agotamiento = (datetime.now() + timedelta(days=dias_agotamiento)).strftime('%Y-%m-%d')
                        urgencia = 'CRÍTICO' if dias_agotamiento <= 7 else 'MEDIO' if dias_agotamiento <= 30 else 'BAJO'
                    else:
                        fecha_agotamiento = 'No se prevé agotamiento'
                        urgencia = 'BAJO'
                    
                    predicciones_agotamiento.append({
                        'id': producto['id'],
                        'nombre': producto['nombre'],
                        'stock_actual': producto['stock_actual'],
                        'categoria': producto['categoria_nombre'],
                        'proveedor': producto['proveedor_nombre'],
                        'dias_hasta_agotamiento': dias_agotamiento if dias_agotamiento < 999 else None,
                        'fecha_agotamiento_estimada': fecha_agotamiento,
                        'promedio_ventas_diarias': round(promedio_diario, 2),
                        'nivel_urgencia': urgencia
                    })
            
            cursor.close()
            
            # Ordenar por urgencia (críticos primero)
            predicciones_agotamiento.sort(key=lambda x: (
                0 if x['nivel_urgencia'] == 'CRÍTICO' else
                1 if x['nivel_urgencia'] == 'MEDIO' else 2,
                x['dias_hasta_agotamiento'] or 999
            ))
            
            return {
                'success': True,
                'data': predicciones_agotamiento,
                'total_productos': len(predicciones_agotamiento),
                'fecha_reporte': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al generar predicción de agotamiento: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def obtener_reporte_sobrestock():
        """
        Identifica productos con exceso de inventario
        """
        try:
            cursor = mysql.connection.cursor()
            
            # Obtener productos con stock alto
            query = """
            SELECT 
                p.id, p.nombre, p.stock_actual, p.precio_compra,
                c.nombre as categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.activo = 1 AND p.stock_actual > 0
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            productos_sobrestock = []
            
            for producto in productos:
                # Obtener ventas últimos 60 días
                ventas_query = """
                SELECT 
                    DATE(f.fecha_factura) as fecha,
                    SUM(df.cantidad) as cantidad
                FROM detalle_factura df
                JOIN facturas f ON df.factura_id = f.id
                WHERE df.producto_id = %s
                    AND f.fecha_factura >= DATE_SUB(NOW(), INTERVAL 60 DAY)
                GROUP BY DATE(f.fecha_factura)
                """
                
                cursor.execute(ventas_query, (producto['id'],))
                ventas = cursor.fetchall()
                
                if ventas:
                    ventas_data = [
                        {
                            'fecha': venta['fecha'].strftime('%Y-%m-%d'),
                            'cantidad': int(venta['cantidad'])
                        }
                        for venta in ventas
                    ]
                    
                    promedio_diario = calcular_promedio_movil(ventas_data, 60)
                    analisis_sobrestock = detectar_sobrestock(
                        producto['stock_actual'], 
                        promedio_diario, 
                        60  # 60 días es excesivo
                    )
                    
                    if analisis_sobrestock['es_sobrestock']:
                        valor_exceso = analisis_sobrestock['dias_sobrantes'] * promedio_diario * float(producto['precio_compra'])
                        
                        productos_sobrestock.append({
                            'id': producto['id'],
                            'nombre': producto['nombre'],
                            'stock_actual': producto['stock_actual'],
                            'categoria': producto['categoria_nombre'],
                            'promedio_ventas_diarias': round(promedio_diario, 2),
                            'dias_sobrantes': analisis_sobrestock['dias_sobrantes'],
                            'unidades_exceso': int(analisis_sobrestock['dias_sobrantes'] * promedio_diario),
                            'valor_exceso': round(valor_exceso, 2),
                            'sugerencia': analisis_sobrestock['sugerencia']
                        })
            
            cursor.close()
            
            # Ordenar por valor de exceso (mayor impacto primero)
            productos_sobrestock.sort(key=lambda x: x['valor_exceso'], reverse=True)
            
            return {
                'success': True,
                'data': productos_sobrestock,
                'total_productos': len(productos_sobrestock),
                'valor_total_exceso': sum(p['valor_exceso'] for p in productos_sobrestock),
                'fecha_reporte': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al generar reporte de sobrestock: {str(e)}',
                'data': []
            }
    
    @staticmethod
    def obtener_reporte_rotacion_productos():
        """
        Analiza la rotación de inventario de todos los productos
        """
        try:
            cursor = mysql.connection.cursor()
            
            # Obtener productos con datos de inventario
            query = """
            SELECT 
                p.id, p.nombre, p.stock_actual, p.precio_venta,
                c.nombre as categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.activo = 1
            """
            
            cursor.execute(query)
            productos = cursor.fetchall()
            
            analisis_rotacion = []
            
            for producto in productos:
                # Obtener ventas últimos 90 días para calcular rotación
                ventas_query = """
                SELECT 
                    SUM(df.cantidad) as total_vendido,
                    COUNT(DISTINCT DATE(f.fecha_factura)) as dias_con_ventas
                FROM detalle_factura df
                JOIN facturas f ON df.factura_id = f.id
                WHERE df.producto_id = %s
                    AND f.fecha_factura >= DATE_SUB(NOW(), INTERVAL 90 DAY)
                """
                
                cursor.execute(ventas_query, (producto['id'],))
                resultado_ventas = cursor.fetchone()
                
                total_vendido = resultado_ventas['total_vendido'] or 0
                
                if total_vendido > 0:
                    # Calcular stock promedio (simplificado)
                    stock_promedio = producto['stock_actual'] + (total_vendido / 2)
                    
                    # Calcular rotación usando algoritmo IA
                    rotacion_info = calcular_rotacion_producto(total_vendido, stock_promedio)
                    
                    # Calcular ingresos generados
                    ingresos_90_dias = total_vendido * float(producto['precio_venta'])
                    
                    analisis_rotacion.append({
                        'id': producto['id'],
                        'nombre': producto['nombre'],
                        'categoria': producto['categoria_nombre'],
                        'stock_actual': producto['stock_actual'],
                        'total_vendido_90_dias': total_vendido,
                        'rotacion': rotacion_info['rotacion'],
                        'velocidad_rotacion': rotacion_info['velocidad'],
                        'ingresos_90_dias': round(ingresos_90_dias, 2),
                        'dias_con_ventas': resultado_ventas['dias_con_ventas'],
                        'frecuencia_ventas': round((resultado_ventas['dias_con_ventas'] / 90) * 100, 1)
                    })
            
            cursor.close()
            
            # Ordenar por rotación (más alta primero)
            analisis_rotacion.sort(key=lambda x: x['rotacion'], reverse=True)
            
            return {
                'success': True,
                'data': analisis_rotacion,
                'total_productos': len(analisis_rotacion),
                'resumen': {
                    'productos_rapidos': len([p for p in analisis_rotacion if p['velocidad_rotacion'] in ['Muy Rápida', 'Rápida']]),
                    'productos_lentos': len([p for p in analisis_rotacion if p['velocidad_rotacion'] in ['Lenta', 'Muy Lenta']]),
                    'ingresos_totales_90_dias': sum(p['ingresos_90_dias'] for p in analisis_rotacion)
                },
                'fecha_reporte': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al generar reporte de rotación: {str(e)}',
                'data': []
            }