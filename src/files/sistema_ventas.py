"""sistema_ventas.py
Clase SistemaDeVentas — gestiona catálogo de productos y registro de ventas.
Ahora carga todas las columnas del CSV de Shopping Trends.
"""
from typing import List, Optional
import pandas as pd

from producto import Producto
from venta import Venta
from exceptions import ProductoInvalido, VentaInvalida, ArchivoNoEncontrado


# Mapeo columna CSV → parámetro
_COL = {
    "item":          "Item Purchased",
    "precio":        "Purchase Amount (USD)",
    "categoria":     "Category",
    "color":         "Color",
    "talla":         "Size",
    "suscripcion":   "Subscription Status",
    "edad":          "Age",
    "genero":        "Gender",
    "ubicacion":     "Location",
    "metodo_pago":   "Payment Method",
    "tipo_envio":    "Shipping Type",
    "descuento":     "Discount Applied",
    "codigo_promo":  "Promo Code Used",
    "calificacion":  "Review Rating",
    "frecuencia":    "Frequency of Purchases",
    "compras_prev":  "Previous Purchases",
    "temporada":     "Season",
    "cantidad":      "Item Purchased",   # cada fila = 1 compra
}


class SistemaDeVentas:
    def __init__(self):
        self._productos: List[Producto] = []
        self._ventas:    List[Venta]    = []

    # ── Registro ──────────────────────────────────────────────────

    def registrar_producto(self, producto: Producto) -> bool:
        """Agrega producto si no existe. Retorna True si fue nuevo."""
        if not isinstance(producto, Producto):
            raise ProductoInvalido("Objeto no es un Producto válido.")
        nombre = producto.get_nombre().strip().lower()
        if any(p.get_nombre().strip().lower() == nombre for p in self._productos):
            return False
        self._productos.append(producto)
        return True

    def registrar_venta(self, venta: Venta) -> None:
        if not isinstance(venta, Venta):
            raise VentaInvalida("Objeto no es una Venta válida.")
        self._ventas.append(venta)

    # ── Listados ──────────────────────────────────────────────────

    def listar_productos(self) -> None:
        if not self._productos:
            print("No hay productos registrados.")
            return
        for i, p in enumerate(self._productos, 1):
            print(f"{i}. {p}")

    def listar_ventas(self) -> None:
        if not self._ventas:
            print("No hay ventas registradas.")
            return
        for i, v in enumerate(self._ventas, 1):
            print(f"{i}. {v}")

    # ── DataFrame ─────────────────────────────────────────────────

    def obtener_dataframe(self) -> pd.DataFrame:
        """Construye un DataFrame completo con todos los campos de cada venta."""
        if not self._ventas:
            return pd.DataFrame()
        rows = []
        for v in self._ventas:
            p = v.get_producto()
            rows.append({
                "producto":          p.get_nombre(),
                "categoria":         p.get_categoria(),
                "color":             p.get_color(),
                "talla":             p.get_talla(),
                "suscripcion":       p.get_suscripcion(),
                "cantidad":          v.get_cantidad(),
                "precio_unitario":   p.get_precio_unitario(),
                "total":             v.get_monto(),
                "temporada":         v.get_temporada(),
                "edad":              v.get_edad(),
                "genero":            v.get_genero(),
                "ubicacion":         v.get_ubicacion(),
                "metodo_pago":       v.get_metodo_pago(),
                "tipo_envio":        v.get_tipo_envio(),
                "descuento":         v.get_descuento(),
                "codigo_promo":      v.get_codigo_promo(),
                "calificacion":      v.get_calificacion(),
                "frecuencia_compra": v.get_frecuencia_compra(),
                "compras_previas":   v.get_compras_previas(),
            })
        return pd.DataFrame(rows)

    # ── Getters ───────────────────────────────────────────────────

    def obtener_productos(self) -> List[Producto]:
        return list(self._productos)

    def obtener_ventas(self) -> List[Venta]:
        return list(self._ventas)

    # ── Carga CSV ────────────────────────────────────────────────

    def cargar_csv(self, ruta: str) -> None:
        """Carga el CSV de Shopping Trends (18 columnas)."""
        try:
            df = pd.read_csv(ruta)
        except FileNotFoundError:
            raise ArchivoNoEncontrado(f"Archivo no encontrado: {ruta}")

        # Normalizar booleanos
        def to_bool(val) -> bool:
            return str(val).strip().lower() in ("yes", "true", "1")

        for _, fila in df.iterrows():
            nombre   = str(fila.get("Item Purchased", "")).strip()
            precio   = float(fila.get("Purchase Amount (USD)", 0) or 0)
            categoria = str(fila.get("Category", "General")).strip()
            color    = str(fila.get("Color", "")).strip()
            talla    = str(fila.get("Size", "")).strip()
            suscripcion = to_bool(fila.get("Subscription Status", False))

            # Crear / reusar producto
            p = Producto(nombre, precio, categoria, color, talla, suscripcion)
            self.registrar_producto(p)
            producto_reg = self._buscar_producto(nombre)

            # Venta con todos los campos demográficos
            v = Venta(
                producto      = producto_reg,
                cantidad      = 1,
                temporada     = str(fila.get("Season", "General")).strip(),
                monto         = precio,
                edad          = int(fila.get("Age", 0) or 0),
                genero        = str(fila.get("Gender", "")).strip(),
                ubicacion     = str(fila.get("Location", "")).strip(),
                metodo_pago   = str(fila.get("Payment Method", "")).strip(),
                tipo_envio    = str(fila.get("Shipping Type", "")).strip(),
                descuento     = to_bool(fila.get("Discount Applied", False)),
                codigo_promo  = to_bool(fila.get("Promo Code Used", False)),
                calificacion  = float(fila.get("Review Rating", 0) or 0),
                frecuencia_compra = str(fila.get("Frequency of Purchases", "")).strip(),
                compras_previas   = int(fila.get("Previous Purchases", 0) or 0),
            )
            self.registrar_venta(v)

    def _buscar_producto(self, nombre: str) -> Producto:
        nombre_lower = nombre.strip().lower()
        for p in self._productos:
            if p.get_nombre().strip().lower() == nombre_lower:
                return p
        raise ProductoInvalido(f"Producto '{nombre}' no encontrado.")
