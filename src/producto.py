from exceptions import ProductoInvalido

class Producto:
    def __init__(self, nombre: str, precio_unitario: float, categoria: str = "General"):
        if not isinstance(nombre, str):
            raise ProductoInvalido("El nombre del producto debe ser una cadena de texto.")
        nombre = nombre.strip()
        if nombre == "":
            raise ProductoInvalido("El nombre del producto no puede estar vacío.")
        if not isinstance(precio_unitario, (int, float)):
            raise ProductoInvalido("El precio unitario debe ser numérico.")
        if precio_unitario <= 0:
            raise ProductoInvalido("El precio debe ser mayor a 0.")
        if not isinstance(categoria, str):
            raise ProductoInvalido("La categoría debe ser una cadena de texto.")
        categoria = categoria.strip()
        if categoria == "":
            raise ProductoInvalido("La categoría no puede estar vacía.")
        self._nombre = nombre
        self._precio_unitario = float(precio_unitario)
        self._categoria = categoria

    def get_nombre(self) -> str:
        return self._nombre

    def get_precio_unitario(self) -> float:
        return self._precio_unitario

    def get_categoria(self) -> str:
        return self._categoria

    def __str__(self) -> str:
        return f"{self._nombre} [{self._categoria}] (${self._precio_unitario:,.2f})"