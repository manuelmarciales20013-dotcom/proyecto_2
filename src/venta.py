"""venta.py
Clase Venta — composición con Producto.
Cada venta guarda el producto, la cantidad, la temporada y el precio de compra.
"""
from exceptions import VentaInvalida
from producto import Producto


class Venta:
    def __init__(self, producto: Producto, cantidad: float,
                 temporada: str = "General", monto: float = 0.0):
        # Validaciones
        if not isinstance(producto, Producto):
            raise VentaInvalida("La venta debe contener un objeto Producto válido.")
        if not isinstance(cantidad, (int, float)):
            raise VentaInvalida("La cantidad debe ser numérica y mayor que 0.")
        if cantidad <= 0:
            raise VentaInvalida("La cantidad debe ser mayor que 0.")
        if not isinstance(temporada, str):
            raise VentaInvalida("La temporada debe ser una cadena de texto.")
        temporada = temporada.strip()
        if temporada == "":
            raise VentaInvalida("La temporada no puede estar vacía.")

        # Atributos privados
        self._producto = producto
        self._cantidad = int(cantidad)
        self._temporada = temporada
        # monto: precio real de compra (viene del CSV, columna Purchase Amount)
        self._monto = float(monto) if monto > 0 else float(producto.get_precio_unitario())

    # Getters
    def get_producto(self) -> Producto:
        return self._producto

    def get_cantidad(self) -> float:
        return self._cantidad

    def get_temporada(self) -> str:
        return self._temporada

    def get_monto(self) -> float:
        return self._monto

    def calcular_total(self) -> float:
        """Total de la venta: cantidad × precio unitario."""
        return self._cantidad * self._producto.get_precio_unitario()

    def __str__(self) -> str:
        return (f"{self._cantidad} × {self._producto.get_nombre()} "
                f"({self._temporada}) = ${self._monto:,.2f}")
