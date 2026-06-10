"""exceptions.py
Jerarquía de excepciones del Sistema de Ventas.
"""


class ErrorSistemaVentas(Exception):
    """Base de todas las excepciones del sistema."""
    def __init__(self, mensaje: str, detalle: str = ""):
        super().__init__(mensaje)
        self.detalle = detalle

    def __str__(self):
        base = super().__str__()
        return f"{base} — {self.detalle}" if self.detalle else base


class ProductoInvalido(ErrorSistemaVentas):
    """Datos de producto incorrectos o faltantes."""


class VentaInvalida(ErrorSistemaVentas):
    """Datos de venta incorrectos o faltantes."""


class DatosInvalidos(ErrorSistemaVentas):
    """Error genérico de datos de entrada."""


class ArchivoNoEncontrado(ErrorSistemaVentas):
    """El archivo CSV o de exportación no existe."""


class ExportacionError(ErrorSistemaVentas):
    """Falló la exportación de un reporte."""
