# backend/app/routes/productos.py
from flask import Blueprint, jsonify,request
from app.database import mysql

# Creamos el blueprint para productos
productos_bp = Blueprint('productos', __name__)

# Ruta para listar todos los productos
@productos_bp.route('/productos', methods=['GET'])
def listar_productos():
    cursor = mysql.connection.cursor()
    
    # Consulta SQL con JOIN para traer nombres de categoría y proveedor
    query = """
    SELECT 
        p.id, p.nombre, p.descripcion, p.precio_compra, p.precio_venta,
        p.stock_actual, p.stock_minimo,
        c.nombre as categoria_nombre,
        pr.nombre as proveedor_nombre
    FROM productos p
    LEFT JOIN categorias c ON p.categoria_id = c.id
    LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
    """
    
    cursor.execute(query)
    productos = cursor.fetchall()
    cursor.close()
    
    return jsonify({"productos": productos})

# Ruta para ver un producto específico
@productos_bp.route('/productos/<int:producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    cursor = mysql.connection.cursor()
    
    # Consulta SQL para un producto específico
    query = """
    SELECT 
        p.id, p.nombre, p.descripcion, p.precio_compra, p.precio_venta,
        p.stock_actual, p.stock_minimo,
        c.nombre as categoria_nombre,
        pr.nombre as proveedor_nombre
    FROM productos p
    LEFT JOIN categorias c ON p.categoria_id = c.id
    LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
    WHERE p.id = %s
    """
    
    cursor.execute(query, (producto_id,))
    producto = cursor.fetchone()
    cursor.close()
    
    # Si no encuentra el producto
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
    
    return jsonify({"producto": producto})

# Ruta para agregar un producto nuevo- para esto tuvimos que importar 
#request 
@productos_bp.route('/productos', methods=['POST'])
def agregar_producto():
    # Obtener datos del JSON enviado
    data = request.get_json()
    
    # Validar que vengan los campos obligatorios
    campos_requeridos = ['nombre', 'precio_compra', 'precio_venta', 'stock_actual', 'stock_minimo', 'categoria_id', 'proveedor_id']
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({"error": f"Campo '{campo}' es requerido"}), 400
    
    cursor = mysql.connection.cursor()
    
    # Query para insertar el producto
    query = """
    INSERT INTO productos (nombre, descripcion, precio_compra, precio_venta, 
                          stock_actual, stock_minimo, categoria_id, proveedor_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    valores = (
        data['nombre'],
        data.get('descripcion', ''),  # Opcional
        data['precio_compra'],
        data['precio_venta'],
        data['stock_actual'],
        data['stock_minimo'],
        data['categoria_id'],
        data['proveedor_id']  
    )
    
    cursor.execute(query, valores)
    mysql.connection.commit()
    
    # Obtener el ID del producto recién creado
    producto_id = cursor.lastrowid
    cursor.close()
    
    return jsonify({
        "mensaje": "Producto agregado exitosamente",
        "producto_id": producto_id
    }), 201
    
@productos_bp.route('/productos/<int:producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    cursor = mysql.connection.cursor()
    
    # Verificar que el producto existe
    cursor.execute("SELECT id FROM productos WHERE id = %s", (producto_id,))
    producto = cursor.fetchone()
    
    if not producto:
        cursor.close()
        return jsonify({"error": "Producto no encontrado"}), 404
    
    # Eliminar el producto
    cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({"mensaje": f"Producto {producto_id} eliminado exitosamente"}), 200    