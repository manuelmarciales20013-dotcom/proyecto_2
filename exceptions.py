class ErrorSistemaVentas(Exception):
    """Clase base para las excepciones del sistema de ventas."""
    pass

class ProductoInvalido(ErrorSistemaVentas):
    pass

class VentaInvalida(ErrorSistemaVentas):
    pass

class DatosInvalidos(ErrorSistemaVentas):
    pass

