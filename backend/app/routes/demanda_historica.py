from flask import Blueprint, request, jsonify
from app.database import mysql

demanda_historica_bp = Blueprint('demanda_historica', __name__)

# Listar todo el historial de demanda
@demanda_historica_bp.route('/demanda-historica', methods=['GET'])
def listar_demanda():
    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT id, producto_id, fecha, cantidad_vendida
            FROM demanda_historica
            ORDER BY fecha DESC
        """
        cursor.execute(query)
        demanda = cursor.fetchall()
        cursor.close()
        return jsonify({'success': True, 'data': demanda, 'total': len(demanda)}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al obtener demanda histórica: {str(e)}'}), 500

# Obtener un registro específico
@demanda_historica_bp.route('/demanda-historica/<int:id>', methods=['GET'])
def obtener_demanda(id):
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT id, producto_id, fecha, cantidad_vendida FROM demanda_historica WHERE id = %s"
        cursor.execute(query, (id,))
        registro = cursor.fetchone()
        cursor.close()
        if not registro:
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        return jsonify({'success': True, 'data': registro}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al obtener registro: {str(e)}'}), 500

# Crear un nuevo registro
@demanda_historica_bp.route('/demanda-historica', methods=['POST'])
def crear_demanda():
    try:
        data = request.get_json()
        campos_requeridos = ['producto_id', 'fecha', 'cantidad_vendida']
        for campo in campos_requeridos:
            if campo not in data or data[campo] is None:
                return jsonify({'success': False, 'message': f'El campo {campo} es requerido'}), 400
        cursor = mysql.connection.cursor()
        query = """
            INSERT INTO demanda_historica (producto_id, fecha, cantidad_vendida)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (data['producto_id'], data['fecha'], data['cantidad_vendida']))
        mysql.connection.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        return jsonify({'success': True, 'data': {'id': nuevo_id}, 'message': 'Registro creado exitosamente'}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al crear registro: {str(e)}'}), 500

# Actualizar un registro existente
@demanda_historica_bp.route('/demanda-historica/<int:id>', methods=['PATCH'])
def actualizar_demanda(id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No se enviaron datos para actualizar'}), 400
        campos_permitidos = ['producto_id', 'fecha', 'cantidad_vendida']
        campos_actualizar = []
        valores = []
        for campo in campos_permitidos:
            if campo in data:
                campos_actualizar.append(f"{campo} = %s")
                valores.append(data[campo])
        if not campos_actualizar:
            return jsonify({'success': False, 'message': 'No hay campos válidos para actualizar'}), 400
        valores.append(id)
        cursor = mysql.connection.cursor()
        query = f"UPDATE demanda_historica SET {', '.join(campos_actualizar)} WHERE id = %s"
        cursor.execute(query, valores)
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Registro actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al actualizar registro: {str(e)}'}), 500

# Eliminar un registro
@demanda_historica_bp.route('/demanda-historica/<int:id>', methods=['DELETE'])
def eliminar_demanda(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM demanda_historica WHERE id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        cursor.execute("DELETE FROM demanda_historica WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Registro eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al eliminar registro: {str(e)}'}), 500
