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

@productos_bp.route('/productos/<int:producto_id>', methods=['PATCH'])
def actualizar_producto(producto_id):
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No se enviaron datos para actualizar"}), 400
    
    cursor = mysql.connection.cursor()
    
    # Verificar que el producto existe
    cursor.execute("SELECT id FROM productos WHERE id = %s", (producto_id,))
    producto = cursor.fetchone()
    
    if not producto:
        cursor.close()
        return jsonify({"error": "Producto no encontrado"}), 404
    
    # Campos que se pueden actualizar
    campos_permitidos = ['nombre', 'descripcion', 'precio_compra', 'precio_venta', 
                        'stock_actual', 'stock_minimo', 'categoria_id', 'proveedor_id']
    
    # Construir la query dinámicamente
    campos_actualizar = []
    valores = []
    
    for campo in campos_permitidos:
        if campo in data:
            campos_actualizar.append(f"{campo} = %s")
            valores.append(data[campo])
    
    if not campos_actualizar:
        cursor.close()
        return jsonify({"error": "No se especificaron campos válidos para actualizar"}), 400
    
    # Agregar el ID al final para el WHERE
    valores.append(producto_id)
    
    # Ejecutar la actualización
    query = f"UPDATE productos SET {', '.join(campos_actualizar)} WHERE id = %s"
    cursor.execute(query, valores)
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({"mensaje": f"Producto {producto_id} actualizado exitosamente"}), 200

# las siguientes 3 rutas son para obtener productos con stock bajo, por categoría y por proveedor, m
# es más que todo para poder filtrar los productos de una mejor manera
 
@productos_bp.route('/productos/stock-bajo', methods=['GET'])
def productos_stock_bajo():
    cursor = mysql.connection.cursor()
    
    # Productos con stock actual <= stock mínimo
    query = """
    SELECT p.id, p.nombre, p.descripcion, p.precio_compra, p.precio_venta,
           p.stock_actual, p.stock_minimo, 
           c.nombre as categoria, pr.nombre as proveedor,
           (p.stock_actual - p.stock_minimo) as diferencia
    FROM productos p
    LEFT JOIN categorias c ON p.categoria_id = c.id
    LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
    WHERE p.stock_actual <= p.stock_minimo
    ORDER BY (p.stock_actual - p.stock_minimo) ASC, p.stock_actual ASC
    """
    
    cursor.execute(query)
    productos = cursor.fetchall()
    cursor.close()
    
    if not productos:
        return jsonify({
            "mensaje": "No hay productos con stock bajo",
            "productos_stock_bajo": []
        }), 200
    
    return jsonify({
        "mensaje": f"Se encontraron {len(productos)} productos con stock bajo",
        "productos_stock_bajo": productos
    }), 200


@productos_bp.route('/productos/categoria/<int:categoria_id>', methods=['GET'])
def productos_por_categoria(categoria_id):
    cursor = mysql.connection.cursor()
    
    # Verificar que la categoría existe
    cursor.execute("SELECT nombre FROM categorias WHERE id = %s", (categoria_id,))
    categoria = cursor.fetchone()
    
    if not categoria:
        cursor.close()
        return jsonify({"error": "Categoría no encontrada"}), 404
    
    # Obtener productos de la categoría
    query = """
    SELECT p.id, p.nombre, p.descripcion, p.precio_compra, p.precio_venta,
           p.stock_actual, p.stock_minimo, 
           c.nombre as categoria, pr.nombre as proveedor
    FROM productos p
    LEFT JOIN categorias c ON p.categoria_id = c.id
    LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
    WHERE p.categoria_id = %s
    ORDER BY p.nombre ASC
    """
    
    cursor.execute(query, (categoria_id,))
    productos = cursor.fetchall()
    cursor.close()
    
    return jsonify({
        "categoria": categoria[0],
        "categoria_id": categoria_id,
        "total_productos": len(productos),
        "productos": productos
    }), 200


@productos_bp.route('/productos/proveedor/<int:proveedor_id>', methods=['GET'])
def productos_por_proveedor(proveedor_id):
    cursor = mysql.connection.cursor()
    
    # Verificar que el proveedor existe
    cursor.execute("SELECT nombre FROM proveedores WHERE id = %s", (proveedor_id,))
    proveedor = cursor.fetchone()
    
    if not proveedor:
        cursor.close()
        return jsonify({"error": "Proveedor no encontrado"}), 404
    
    # Obtener productos del proveedor
    query = """
    SELECT p.id, p.nombre, p.descripcion, p.precio_compra, p.precio_venta,
           p.stock_actual, p.stock_minimo, 
           c.nombre as categoria, pr.nombre as proveedor
    FROM productos p
    LEFT JOIN categorias c ON p.categoria_id = c.id
    LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
    WHERE p.proveedor_id = %s
    ORDER BY p.nombre ASC
    """
    
    cursor.execute(query, (proveedor_id,))
    productos = cursor.fetchall()
    cursor.close()
    
    return jsonify({
        "proveedor": proveedor[0],
        "proveedor_id": proveedor_id,
        "total_productos": len(productos),
        "productos": productos
    }), 200