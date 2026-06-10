"""venta.py
Clase Venta — composición con Producto.
Ahora captura todos los campos demográficos y transaccionales del CSV:
  edad, genero, ubicacion, metodo_pago, tipo_envio, descuento,
  codigo_promo, calificacion, frecuencia_compra, compras_previas.
"""
from exceptions import VentaInvalida
from producto import Producto

METODOS_PAGO_VALIDOS = {"Credit Card", "Debit Card", "Cash", "PayPal",
                         "Venmo", "Bank Transfer", ""}
TIPOS_ENVIO_VALIDOS = {"Free Shipping", "Standard", "Express",
                        "Next Day Air", "2-Day Shipping", "Store Pickup", ""}


class Venta:
    def __init__(
        self,
        producto: Producto,
        cantidad: float,
        temporada: str = "General",
        monto: float = 0.0,
        # ── nuevos campos demográficos / transaccionales ──
        edad: int = 0,
        genero: str = "",
        ubicacion: str = "",
        metodo_pago: str = "",
        tipo_envio: str = "",
        descuento: bool = False,
        codigo_promo: bool = False,
        calificacion: float = 0.0,
        frecuencia_compra: str = "",
        compras_previas: int = 0,
    ):
        # ── Validaciones básicas ─────────────────────────────────
        if not isinstance(producto, Producto):
            raise VentaInvalida("Se requiere un objeto Producto válido.")
        if not isinstance(cantidad, (int, float)) or cantidad <= 0:
            raise VentaInvalida("La cantidad debe ser > 0.", f"recibido: {cantidad}")
        temporada = str(temporada).strip()
        if not temporada:
            raise VentaInvalida("La temporada no puede estar vacía.")

        # ── Validación de calificación ───────────────────────────
        calificacion = float(calificacion) if calificacion else 0.0
        if calificacion < 0 or calificacion > 5:
            calificacion = 0.0   # valor fuera de rango → ignorar

        # ── Atributos privados ───────────────────────────────────
        self._producto          = producto
        self._cantidad          = int(cantidad)
        self._temporada         = temporada
        self._monto             = float(monto) if monto > 0 else producto.get_precio_unitario()
        self._edad              = int(edad) if edad else 0
        self._genero            = str(genero).strip()
        self._ubicacion         = str(ubicacion).strip()
        self._metodo_pago       = str(metodo_pago).strip()
        self._tipo_envio        = str(tipo_envio).strip()
        self._descuento         = bool(descuento)
        self._codigo_promo      = bool(codigo_promo)
        self._calificacion      = calificacion
        self._frecuencia_compra = str(frecuencia_compra).strip()
        self._compras_previas   = int(compras_previas) if compras_previas else 0

    # ── Getters ─────────────────────────────────────────────────
    def get_producto(self) -> Producto:        return self._producto
    def get_cantidad(self) -> int:             return self._cantidad
    def get_temporada(self) -> str:            return self._temporada
    def get_monto(self) -> float:              return self._monto
    def get_edad(self) -> int:                 return self._edad
    def get_genero(self) -> str:              return self._genero
    def get_ubicacion(self) -> str:            return self._ubicacion
    def get_metodo_pago(self) -> str:          return self._metodo_pago
    def get_tipo_envio(self) -> str:           return self._tipo_envio
    def get_descuento(self) -> bool:           return self._descuento
    def get_codigo_promo(self) -> bool:        return self._codigo_promo
    def get_calificacion(self) -> float:       return self._calificacion
    def get_frecuencia_compra(self) -> str:    return self._frecuencia_compra
    def get_compras_previas(self) -> int:      return self._compras_previas

    def calcular_total(self) -> float:
        """Cantidad × precio unitario del producto."""
        return self._cantidad * self._producto.get_precio_unitario()

    def __str__(self) -> str:
        genero_str = f" | {self._genero}" if self._genero else ""
        edad_str   = f", {self._edad} años" if self._edad else ""
        return (
            f"{self._cantidad} × {self._producto.get_nombre()} "
            f"({self._temporada}{genero_str}{edad_str}) = ${self._monto:,.2f}"
        )
