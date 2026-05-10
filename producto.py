from exceptions import ProductoInvalido

class Producto:
    def __init__(self, nombre: str, precio_unitario: float):
        if not isinstance(nombre, str):
            raise ProductoInvalido("El nombre del producto debe ser una cadena de texto.")
        nombre = nombre.strip()
        if nombre == "":
            raise ProductoInvalido("El nombre del producto no puede estar vacío.")
        if not isinstance(precio_unitario, (int, float)):
            raise ProductoInvalido("El precio unitario debe ser numérico.")
        if precio_unitario <= 0:
            raise ProductoInvalido("El precio debe ser mayor a 0.")
        self._nombre = nombre
        self._precio_unitario = float(precio_unitario)

    def get_nombre(self) -> str:
        return self._nombre

    def get_precio_unitario(self) -> float:
        return self._precio_unitario

    def __str__(self) -> str:
        return f"{self._nombre} (${self._precio_unitario:,.2f})"

       