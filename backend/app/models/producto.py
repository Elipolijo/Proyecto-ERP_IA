class Producto:
    def __init__(self, id_producto, codigo, precio, cantidad):
        self.id_producto = id_producto
        self.codigo = codigo
        self.nombre = nombre
        self.precio_compra = precio
        self.cantidad = cantidad

    def __repr__(self):
        return f"Producto(id_producto={self.id_producto}, nombre='{self.nombre}', precio={self.precio}, cantidad={self.cantidad})"