from exceptions import VentaInvalida
from producto import Producto

class venta:
    def __init__(self, nombre:Producto, cantidad: float):
        if cantidad == 0:
            raise VentaInvalida("La cantidad debe ser mayor a 0")
        
        self.nombre = nombre
        self.cantidad = cantidad


