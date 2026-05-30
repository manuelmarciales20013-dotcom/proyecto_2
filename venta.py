from exceptions import VentaInvalida
from producto import Producto

class Venta:
    def __init__(self, producto: Producto, cantidad: float, tienda: str = "General"):
        if not isinstance(producto, Producto):
            raise VentaInvalida("La venta debe contener un objeto Producto válido.")
        if not isinstance(cantidad, (int, float)):
            raise VentaInvalida("La cantidad debe ser numérica y mayor que 0.")
        if cantidad <= 0:
            raise VentaInvalida("La cantidad debe ser mayor que 0.")
        if not isinstance(tienda, str):
            raise VentaInvalida("La tienda debe ser una cadena de texto.")
        tienda = tienda.strip()
        if tienda == "":
            raise VentaInvalida("La tienda no puede estar vacía.")
        self._producto = producto
        self._cantidad = int(cantidad) if isinstance(cantidad, int) else float(cantidad)
        self._tienda = tienda

    def get_producto(self) -> Producto:
        return self._producto

    def get_cantidad(self) -> float:
        return self._cantidad

    def get_tienda(self) -> str:
        return self._tienda

    def calcular_total(self) -> float:
        return self._cantidad * self._producto.get_precio_unitario()

    def __str__(self) -> str:
        total = self.calcular_total()
        return f"{self._cantidad} × {self._producto.get_nombre()} ({self._tienda}) = ${total:,.2f}"
