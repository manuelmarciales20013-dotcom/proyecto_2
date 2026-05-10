from typing import List
import pandas as pd

from producto import Producto
from venta import Venta
from exceptions import ProductoInvalido, VentaInvalida


class SistemaDeVentas:
    def __init__(self):
        self._productos: List[Producto] = []
        self._ventas: List[Venta] = []

    def registrar_producto(self, producto: Producto) -> bool:
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

    def obtener_dataframe(self) -> pd.DataFrame:
        rows = []
        for v in self._ventas:
            prod = v.get_producto()
            rows.append({
                "producto": prod.get_nombre(),
                "cantidad": v.get_cantidad(),
                "precio_unitario": prod.get_precio_unitario(),
                "total": v.calcular_total(),
            })
        df = pd.DataFrame(rows)
        return df

    def obtener_productos(self) -> List[Producto]:
        return list(self._productos)

    def obtener_ventas(self) -> List[Venta]:
        return list(self._ventas)

    def cargar_datos_simulados(self, n: int = 30, seed: int | None = None) -> None:
        from generador import generar_catalogo, generar_ventas

        productos = generar_catalogo()
        ventas = generar_ventas(productos, n=n, seed=seed)

        for p in productos:
            self.registrar_producto(p)
        for v in ventas:
            self.registrar_venta(v)
