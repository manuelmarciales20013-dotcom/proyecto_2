"""sistema_ventas.py
Clase SistemaDeVentas — gestiona el catálogo de productos y las ventas.
"""
from typing import List
import pandas as pd

from producto import Producto
from venta import Venta
from exceptions import ProductoInvalido, VentaInvalida


class SistemaDeVentas:
    def __init__(self):
        # Listas privadas que guardan los objetos
        self._productos: List[Producto] = []
        self._ventas: List[Venta] = []

    # ── Registro ──────────────────────────────────────────────────

    def registrar_producto(self, producto: Producto) -> bool:
        """Agrega un producto al catálogo. Evita duplicados por nombre.
        Retorna True si se agregó, False si ya existía."""
        if not isinstance(producto, Producto):
            raise ProductoInvalido("Objeto no es un Producto válido.")
        nombre = producto.get_nombre().strip().lower()
        if any(p.get_nombre().strip().lower() == nombre for p in self._productos):
            return False  # Ya existe, no se agrega
        self._productos.append(producto)
        return True

    def registrar_venta(self, venta: Venta) -> None:
        """Agrega una venta a la lista de ventas."""
        if not isinstance(venta, Venta):
            raise VentaInvalida("Objeto no es una Venta válida.")
        self._ventas.append(venta)

    # ── Listados (para consola / main.py) ─────────────────────────

    def listar_productos(self) -> None:
        if not self._productos:
            print("No hay productos registrados.")
            return
        for i, p in enumerate(self._productos, start=1):
            print(f"{i}. {p}")

    def listar_ventas(self) -> None:
        if not self._ventas:
            print("No hay ventas registradas.")
            return
        for i, v in enumerate(self._ventas, start=1):
            print(f"{i}. {v}")

    # ── DataFrame ─────────────────────────────────────────────────

    def obtener_dataframe(self) -> pd.DataFrame:
        """Construye un DataFrame con los datos de todas las ventas."""
        rows = []
        for v in self._ventas:
            prod = v.get_producto()
            rows.append({
                "producto":        prod.get_nombre(),
                "categoria":       prod.get_categoria(),
                "cantidad":        v.get_cantidad(),
                "precio_unitario": prod.get_precio_unitario(),
                "total":           v.get_monto(),      # monto real del CSV
                "temporada":       v.get_temporada(),
            })
        return pd.DataFrame(rows)

    # ── Getters de listas ─────────────────────────────────────────

    def obtener_productos(self) -> List[Producto]:
        return list(self._productos)

    def obtener_ventas(self) -> List[Venta]:
        return list(self._ventas)

    # ── Carga desde CSV ───────────────────────────────────────────

    def cargar_csv(self, ruta: str) -> None:
        """Carga productos y ventas desde el archivo Ventas.csv."""
        df = pd.read_csv(ruta)
        for _, fila in df.iterrows():
            # Crear producto con nombre, precio y categoría del CSV
            p = Producto(
                str(fila["Item Purchased"]),
                float(fila["Purchase Amount (USD)"]),
                str(fila["Category"])
            )
            self.registrar_producto(p)   # evita duplicados automáticamente

            # Buscar el producto ya registrado (para mantener la composición)
            producto_reg = self._buscar_producto(str(fila["Item Purchased"]))

            # Crear la venta con cantidad=1 por fila (cada fila es 1 compra)
            v = Venta(
                producto_reg,
                cantidad=1,
                temporada=str(fila["Season"]),
                monto=float(fila["Purchase Amount (USD)"])
            )
            self.registrar_venta(v)

    def _buscar_producto(self, nombre: str) -> Producto:
        """Busca un producto por nombre exacto en el catálogo."""
        nombre_lower = nombre.strip().lower()
        for p in self._productos:
            if p.get_nombre().strip().lower() == nombre_lower:
                return p
        raise ProductoInvalido(f"Producto '{nombre}' no encontrado en el catálogo.")
