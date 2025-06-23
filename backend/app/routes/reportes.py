"""
Rutas de Reportes con IA
5 endpoints que devuelven reportes agrupados con períodos automáticos
"""

from flask import Blueprint, jsonify
from app.services.reporte_service import ReporteService

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/stock-critico', methods=['GET'])
def obtener_reporte_stock_critico():
    """
    Reporte de productos con stock crítico
    Agrupado por niveles: Crítico, Medio, Bueno
    """
    try:
        reporte = ReporteService.obtener_reporte_stock_critico()
        
        # Agrupar por niveles de criticidad
        resultado = {
            'fecha_generacion': reporte['fecha_generacion'],
            'resumen': {
                'total_productos': len(reporte['productos']),
                'criticos': len([p for p in reporte['productos'] if p['nivel_criticidad'] == 'CRÍTICO']),
                'medios': len([p for p in reporte['productos'] if p['nivel_criticidad'] == 'MEDIO']),
                'buenos': len([p for p in reporte['productos'] if p['nivel_criticidad'] == 'BUENO'])
            },
            'por_categoria': {},
            'productos_criticos': [p for p in reporte['productos'] if p['nivel_criticidad'] == 'CRÍTICO']
        }
        
        # Agrupar por categoría
        for producto in reporte['productos']:
            categoria = producto['categoria']
            if categoria not in resultado['por_categoria']:
                resultado['por_categoria'][categoria] = {
                    'criticos': 0,
                    'medios': 0,
                    'buenos': 0,
                    'total': 0
                }
            
            nivel = producto['nivel_criticidad'].lower()
            if nivel == 'crítico':
                resultado['por_categoria'][categoria]['criticos'] += 1
            elif nivel == 'medio':
                resultado['por_categoria'][categoria]['medios'] += 1
            else:
                resultado['por_categoria'][categoria]['buenos'] += 1
            
            resultado['por_categoria'][categoria]['total'] += 1
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reportes_bp.route('/prediccion-demanda', methods=['GET'])
def obtener_reporte_prediccion_demanda():
    """
    Reporte de predicción de demanda futura
    Período automático: últimos 30 días para predecir próximos 30 días
    """
    try:
        reporte = ReporteService.obtener_reporte_prediccion_demanda()
        
        # Agrupar por niveles de demanda
        resultado = {
            'periodo_analizado': reporte['periodo_analizado'],
            'prediccion_para': reporte['prediccion_para'],
            'fecha_generacion': reporte['fecha_generacion'],
            'resumen': {
                'total_productos': len(reporte['predicciones']),
                'alta_demanda': len([p for p in reporte['predicciones'] if p['nivel_demanda'] == 'ALTA']),
                'media_demanda': len([p for p in reporte['predicciones'] if p['nivel_demanda'] == 'MEDIA']),
                'baja_demanda': len([p for p in reporte['predicciones'] if p['nivel_demanda'] == 'BAJA'])
            },
            'por_categoria': {},
            'productos_alta_demanda': [p for p in reporte['predicciones'] if p['nivel_demanda'] == 'ALTA']
        }
        
        # Agrupar por categoría
        for prediccion in reporte['predicciones']:
            categoria = prediccion['categoria']
            if categoria not in resultado['por_categoria']:
                resultado['por_categoria'][categoria] = {
                    'alta_demanda': 0,
                    'media_demanda': 0,
                    'baja_demanda': 0,
                    'total_predicho': 0
                }
            
            nivel = prediccion['nivel_demanda'].lower()
            if nivel == 'alta':
                resultado['por_categoria'][categoria]['alta_demanda'] += 1
            elif nivel == 'media':
                resultado['por_categoria'][categoria]['media_demanda'] += 1
            else:
                resultado['por_categoria'][categoria]['baja_demanda'] += 1
            
            resultado['por_categoria'][categoria]['total_predicho'] += prediccion['demanda_predicha']
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reportes_bp.route('/prediccion-agotamiento', methods=['GET'])
def obtener_reporte_prediccion_agotamiento():
    """
    Reporte de predicción de agotamiento
    Período automático: ventas de últimos 15 días
    """
    try:
        reporte = ReporteService.obtener_reporte_prediccion_agotamiento()
        
        # Agrupar por urgencia de agotamiento
        resultado = {
            'periodo_analizado': reporte['periodo_analizado'],
            'fecha_generacion': reporte['fecha_generacion'],
            'resumen': {
                'total_productos': len(reporte['predicciones']),
                'urgente': len([p for p in reporte['predicciones'] if p['urgencia'] == 'URGENTE']),
                'pronto': len([p for p in reporte['predicciones'] if p['urgencia'] == 'PRONTO']),
                'normal': len([p for p in reporte['predicciones'] if p['urgencia'] == 'NORMAL'])
            },
            'por_categoria': {},
            'productos_urgentes': [p for p in reporte['predicciones'] if p['urgencia'] == 'URGENTE']
        }
        
        # Agrupar por categoría
        for prediccion in reporte['predicciones']:
            categoria = prediccion['categoria']
            if categoria not in resultado['por_categoria']:
                resultado['por_categoria'][categoria] = {
                    'urgente': 0,
                    'pronto': 0,
                    'normal': 0,
                    'promedio_dias': 0
                }
            
            urgencia = prediccion['urgencia'].lower()
            if urgencia == 'urgente':
                resultado['por_categoria'][categoria]['urgente'] += 1
            elif urgencia == 'pronto':
                resultado['por_categoria'][categoria]['pronto'] += 1
            else:
                resultado['por_categoria'][categoria]['normal'] += 1
        
        # Calcular promedio de días por categoría
        for categoria in resultado['por_categoria']:
            productos_categoria = [p for p in reporte['predicciones'] if p['categoria'] == categoria]
            if productos_categoria:
                promedio = sum(p['dias_hasta_agotamiento'] for p in productos_categoria) / len(productos_categoria)
                resultado['por_categoria'][categoria]['promedio_dias'] = round(promedio, 1)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reportes_bp.route('/sobrestock', methods=['GET'])
def obtener_reporte_sobrestock():
    """
    Reporte de productos con sobrestock
    Estado actual del inventario
    """
    try:
        reporte = ReporteService.obtener_reporte_sobrestock()
        
        # Agrupar por nivel de sobrestock
        resultado = {
            'fecha_generacion': reporte['fecha_generacion'],
            'resumen': {
                'total_productos': len(reporte['productos']),
                'sobrestock_alto': len([p for p in reporte['productos'] if p['nivel_sobrestock'] == 'ALTO']),
                'sobrestock_medio': len([p for p in reporte['productos'] if p['nivel_sobrestock'] == 'MEDIO']),
                'sobrestock_bajo': len([p for p in reporte['productos'] if p['nivel_sobrestock'] == 'BAJO']),
                'valor_total_inmovilizado': sum(p['valor_inmovilizado'] for p in reporte['productos'])
            },
            'por_categoria': {},
            'productos_alto_sobrestock': [p for p in reporte['productos'] if p['nivel_sobrestock'] == 'ALTO']
        }
        
        # Agrupar por categoría
        for producto in reporte['productos']:
            categoria = producto['categoria']
            if categoria not in resultado['por_categoria']:
                resultado['por_categoria'][categoria] = {
                    'alto': 0,
                    'medio': 0,
                    'bajo': 0,
                    'valor_inmovilizado': 0
                }
            
            nivel = producto['nivel_sobrestock'].lower()
            if nivel == 'alto':
                resultado['por_categoria'][categoria]['alto'] += 1
            elif nivel == 'medio':
                resultado['por_categoria'][categoria]['medio'] += 1
            else:
                resultado['por_categoria'][categoria]['bajo'] += 1
            
            resultado['por_categoria'][categoria]['valor_inmovilizado'] += producto['valor_inmovilizado']
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reportes_bp.route('/rotacion-productos', methods=['GET'])
def obtener_reporte_rotacion_productos():
    """
    Reporte de rotación de productos
    Período automático: último mes (30 días)
    """
    try:
        reporte = ReporteService.obtener_reporte_rotacion_productos()
        
        # Agrupar por velocidad de rotación
        resultado = {
            'periodo_analizado': reporte['periodo_analizado'],
            'fecha_generacion': reporte['fecha_generacion'],
            'resumen': {
                'total_productos': len(reporte['productos']),
                'rotacion_alta': len([p for p in reporte['productos'] if p['velocidad_rotacion'] == 'ALTA']),
                'rotacion_media': len([p for p in reporte['productos'] if p['velocidad_rotacion'] == 'MEDIA']),
                'rotacion_baja': len([p for p in reporte['productos'] if p['velocidad_rotacion'] == 'BAJA']),
                'rotacion_promedio': round(sum(p['indice_rotacion'] for p in reporte['productos']) / len(reporte['productos']), 2)
            },
            'por_categoria': {},
            'productos_alta_rotacion': [p for p in reporte['productos'] if p['velocidad_rotacion'] == 'ALTA'],
            'productos_baja_rotacion': [p for p in reporte['productos'] if p['velocidad_rotacion'] == 'BAJA']
        }
        
        # Agrupar por categoría
        for producto in reporte['productos']:
            categoria = producto['categoria']
            if categoria not in resultado['por_categoria']:
                resultado['por_categoria'][categoria] = {
                    'alta': 0,
                    'media': 0,
                    'baja': 0,
                    'rotacion_promedio': 0
                }
            
            velocidad = producto['velocidad_rotacion'].lower()
            if velocidad == 'alta':
                resultado['por_categoria'][categoria]['alta'] += 1
            elif velocidad == 'media':
                resultado['por_categoria'][categoria]['media'] += 1
            else:
                resultado['por_categoria'][categoria]['baja'] += 1
        
        # Calcular rotación promedio por categoría
        for categoria in resultado['por_categoria']:
            productos_categoria = [p for p in reporte['productos'] if p['categoria'] == categoria]
            if productos_categoria:
                promedio = sum(p['indice_rotacion'] for p in productos_categoria) / len(productos_categoria)
                resultado['por_categoria'][categoria]['rotacion_promedio'] = round(promedio, 2)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reportes_bp.route('/resumen-general', methods=['GET'])
def obtener_resumen_general():
    """
    Resumen ejecutivo de todos los reportes
    Dashboard principal
    """
    try:
        # Obtener todos los reportes
        stock_critico = ReporteService.obtener_reporte_stock_critico()
        sobrestock = ReporteService.obtener_reporte_sobrestock()
        rotacion = ReporteService.obtener_reporte_rotacion_productos()
        
        resultado = {
            'fecha_generacion': stock_critico['fecha_generacion'],
            'alertas_criticas': {
                'productos_sin_stock': len([p for p in stock_critico['productos'] if p['nivel_criticidad'] == 'CRÍTICO']),
                'productos_sobrestock': len([p for p in sobrestock['productos'] if p['nivel_sobrestock'] == 'ALTO']),
                'productos_baja_rotacion': len([p for p in rotacion['productos'] if p['velocidad_rotacion'] == 'BAJA'])
            },
            'metricas_generales': {
                'total_productos_analizados': len(stock_critico['productos']),
                'valor_inventario_inmovilizado': sum(p['valor_inmovilizado'] for p in sobrestock['productos']),
                'indice_rotacion_promedio': round(sum(p['indice_rotacion'] for p in rotacion['productos']) / len(rotacion['productos']), 2)
            },
            'recomendaciones': []
        }
        
        # Generar recomendaciones automáticas
        if resultado['alertas_criticas']['productos_sin_stock'] > 0:
            resultado['recomendaciones'].append({
                'tipo': 'URGENTE',
                'mensaje': f"{resultado['alertas_criticas']['productos_sin_stock']} productos están en stock crítico. Revisar inmediatamente."
            })
        
        if resultado['alertas_criticas']['productos_sobrestock'] > 0:
            resultado['recomendaciones'].append({
                'tipo': 'OPTIMIZACIÓN',
                'mensaje': f"{resultado['alertas_criticas']['productos_sobrestock']} productos tienen sobrestock. Considerar promociones."
            })
        
        if resultado['alertas_criticas']['productos_baja_rotacion'] > 0:
            resultado['recomendaciones'].append({
                'tipo': 'ANÁLISIS',
                'mensaje': f"{resultado['alertas_criticas']['productos_baja_rotacion']} productos tienen baja rotación. Evaluar estrategia comercial."
            })
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        