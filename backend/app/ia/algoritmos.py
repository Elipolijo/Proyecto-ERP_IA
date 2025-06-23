"""
Algoritmos de IA para predicciones de inventario
Funciones matemáticas puras para análisis de datos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calcular_promedio_movil(ventas_data, ventana_dias=30):
    """
    Calcula promedio móvil para predicción de demanda
    
    Args:
        ventas_data: Lista de dict con [{'fecha': '2024-01-01', 'cantidad': 5}, ...]
        ventana_dias: Días para el promedio móvil
    
    Returns:
        float: Promedio de ventas diarias
    """
    if not ventas_data:
        return 0
    
    df = pd.DataFrame(ventas_data)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df = df.sort_values('fecha')
    
    # Si hay pocos datos, usar todos
    if len(df) <= ventana_dias:
        return df['cantidad'].mean()
    
    # Usar solo los últimos N días
    return df['cantidad'].tail(ventana_dias).mean()

def calcular_dias_hasta_agotamiento(stock_actual, promedio_ventas_diarias):
    """
    Calcula cuántos días durará el stock actual
    
    Args:
        stock_actual: Stock disponible
        promedio_ventas_diarias: Promedio de ventas por día
    
    Returns:
        int: Días hasta agotamiento (0 si ya está agotado)
    """
    if stock_actual <= 0:
        return 0
    
    if promedio_ventas_diarias <= 0:
        return 999  # Sin ventas históricas = durará mucho
    
    return int(stock_actual / promedio_ventas_diarias)

def detectar_sobrestock(stock_actual, promedio_ventas_diarias, factor_sobrestock=60):
    """
    Detecta si un producto tiene sobrestock
    
    Args:
        stock_actual: Stock disponible
        promedio_ventas_diarias: Promedio de ventas por día
        factor_sobrestock: Días de stock considerados "excesivos"
    
    Returns:
        dict: {'es_sobrestock': bool, 'dias_sobrantes': int, 'sugerencia': str}
    """
    if promedio_ventas_diarias <= 0:
        return {
            'es_sobrestock': False,
            'dias_sobrantes': 0,
            'sugerencia': 'Sin datos de ventas para evaluar'
        }
    
    dias_stock = stock_actual / promedio_ventas_diarias
    
    if dias_stock > factor_sobrestock:
        return {
            'es_sobrestock': True,
            'dias_sobrantes': int(dias_stock - factor_sobrestock),
            'sugerencia': f'Reducir pedidos por {int(dias_stock - factor_sobrestock)} días'
        }
    
    return {
        'es_sobrestock': False,
        'dias_sobrantes': 0,
        'sugerencia': 'Stock en niveles normales'
    }

def calcular_rotacion_producto(ventas_periodo, stock_promedio):
    """
    Calcula la rotación de inventario (cuántas veces se vendió el stock)
    
    Args:
        ventas_periodo: Total vendido en el período
        stock_promedio: Stock promedio durante el período
    
    Returns:
        dict: {'rotacion': float, 'velocidad': str}
    """
    if stock_promedio <= 0:
        return {'rotacion': 0, 'velocidad': 'Sin stock'}
    
    rotacion = ventas_periodo / stock_promedio
    
    # Clasificar velocidad de rotación
    if rotacion >= 12:  # Más de 12 veces al año
        velocidad = 'Muy Rápida'
    elif rotacion >= 6:  # 6-12 veces al año
        velocidad = 'Rápida'
    elif rotacion >= 3:  # 3-6 veces al año
        velocidad = 'Normal'
    elif rotacion >= 1:  # 1-3 veces al año
        velocidad = 'Lenta'
    else:
        velocidad = 'Muy Lenta'
    
    return {
        'rotacion': round(rotacion, 2),
        'velocidad': velocidad
    }

def identificar_stock_critico(stock_actual, stock_minimo):
    """
    Identifica productos en stock crítico
    
    Args:
        stock_actual: Stock disponible
        stock_minimo: Stock mínimo configurado
    
    Returns:
        dict: {'es_critico': bool, 'nivel_alerta': str, 'accion_sugerida': str}
    """
    if stock_actual <= 0:
        return {
            'es_critico': True,
            'nivel_alerta': 'AGOTADO',
            'accion_sugerida': 'Reponer inmediatamente'
        }
    
    porcentaje = (stock_actual / stock_minimo) * 100 if stock_minimo > 0 else 100
    
    if porcentaje <= 50:  # 50% o menos del mínimo
        return {
            'es_critico': True,
            'nivel_alerta': 'CRÍTICO',
            'accion_sugerida': 'Reponer urgente'
        }
    elif porcentaje <= 100:  # Entre 50% y 100% del mínimo
        return {
            'es_critico': True,
            'nivel_alerta': 'BAJO',
            'accion_sugerida': 'Programar reposición'
        }
    else:
        return {
            'es_critico': False,
            'nivel_alerta': 'NORMAL',
            'accion_sugerida': 'Monitorear'
        }

def predecir_demanda_futura(ventas_data, dias_prediccion=30):
    """
    Predice la demanda futura basada en tendencias históricas
    
    Args:
        ventas_data: Lista de ventas históricas
        dias_prediccion: Días a predecir hacia adelante
    
    Returns:
        dict: {'demanda_estimada': float, 'tendencia': str, 'confianza': str}
    """
    if not ventas_data or len(ventas_data) < 7:
        return {
            'demanda_estimada': 0,
            'tendencia': 'Datos insuficientes',
            'confianza': 'Baja'
        }
    
    df = pd.DataFrame(ventas_data)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df = df.sort_values('fecha')
    
    # Calcular tendencia (comparar primera y segunda mitad)
    mitad = len(df) // 2
    primera_mitad = df.iloc[:mitad]['cantidad'].mean()
    segunda_mitad = df.iloc[mitad:]['cantidad'].mean()
    
    # Promedio móvil de últimos 15 días
    promedio_reciente = df['cantidad'].tail(15).mean()
    
    # Ajustar predicción según tendencia
    if segunda_mitad > primera_mitad * 1.2:
        tendencia = 'Creciente'
        factor_ajuste = 1.1
    elif segunda_mitad < primera_mitad * 0.8:
        tendencia = 'Decreciente'
        factor_ajuste = 0.9
    else:
        tendencia = 'Estable'
        factor_ajuste = 1.0
    
    demanda_estimada = promedio_reciente * factor_ajuste * dias_prediccion
    
    # Evaluar confianza basada en cantidad de datos
    if len(df) >= 30:
        confianza = 'Alta'
    elif len(df) >= 14:
        confianza = 'Media'
    else:
        confianza = 'Baja'
    
    return {
        'demanda_estimada': round(demanda_estimada, 1),
        'tendencia': tendencia,
        'confianza': confianza
    }