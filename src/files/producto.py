"""producto.py
Clase Producto — encapsula los datos del artículo vendido.
Ahora incluye: color, talla y si tiene suscripción activa.
"""
from exceptions import ProductoInvalido

TALLAS_VALIDAS = {"XS", "S", "M", "L", "XL", "XXL", ""}


class Producto:
    def __init__(
        self,
        nombre: str,
        precio_unitario: float,
        categoria: str = "General",
        color: str = "",
        talla: str = "",
        suscripcion: bool = False,
    ):
        # ── Nombre ──────────────────────────────────────────────
        if not isinstance(nombre, str):
            raise ProductoInvalido("El nombre debe ser texto.", f"recibido: {type(nombre)}")
        nombre = nombre.strip()
        if not nombre:
            raise ProductoInvalido("El nombre no puede estar vacío.")

        # ── Precio ──────────────────────────────────────────────
        if not isinstance(precio_unitario, (int, float)):
            raise ProductoInvalido("El precio debe ser numérico.", f"recibido: {type(precio_unitario)}")
        if precio_unitario <= 0:
            raise ProductoInvalido("El precio debe ser > 0.", f"recibido: {precio_unitario}")

        # ── Categoría ───────────────────────────────────────────
        if not isinstance(categoria, str):
            raise ProductoInvalido("La categoría debe ser texto.")
        categoria = categoria.strip()
        if not categoria:
            raise ProductoInvalido("La categoría no puede estar vacía.")

        # ── Color (opcional) ────────────────────────────────────
        color = str(color).strip() if color else ""

        # ── Talla (opcional) ────────────────────────────────────
        talla = str(talla).strip().upper() if talla else ""
        if talla and talla not in TALLAS_VALIDAS:
            # Aceptar cualquier talla desconocida sin lanzar excepción
            pass

        # ── Atributos privados ──────────────────────────────────
        self._nombre = nombre
        self._precio_unitario = float(precio_unitario)
        self._categoria = categoria
        self._color = color
        self._talla = talla
        self._suscripcion = bool(suscripcion)

    # ── Getters ─────────────────────────────────────────────────
    def get_nombre(self) -> str:
        return self._nombre

    def get_precio_unitario(self) -> float:
        return self._precio_unitario

    def get_categoria(self) -> str:
        return self._categoria

    def get_color(self) -> str:
        return self._color

    def get_talla(self) -> str:
        return self._talla

    def get_suscripcion(self) -> bool:
        return self._suscripcion

    # ── Setter de precio (con validación) ───────────────────────
    def set_precio_unitario(self, precio: float) -> None:
        if not isinstance(precio, (int, float)) or precio <= 0:
            raise ProductoInvalido("El precio debe ser > 0.", f"recibido: {precio}")
        self._precio_unitario = float(precio)

    # ── Representación ──────────────────────────────────────────
    def __str__(self) -> str:
        partes = [f"{self._nombre} [{self._categoria}] (${self._precio_unitario:,.2f})"]
        if self._color:
            partes.append(f"Color: {self._color}")
        if self._talla:
            partes.append(f"Talla: {self._talla}")
        if self._suscripcion:
            partes.append("✓ Suscripción")
        return " | ".join(partes)
