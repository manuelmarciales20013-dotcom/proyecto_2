import random
from producto import Producto
from venta import Venta
from typing import List, Tuple


def generar_catalogo() -> List[Producto]:
    productos = [
        Producto("Camisa", 25000),
        Producto("Pantalón", 40000),
        Producto("Zapatos", 60000),
        Producto("Gorra", 15000),
        Producto("Cinturón", 12000),
    ]
    return productos


def generar_ventas(productos: List[Producto], n: int = 30, pesos=None, seed: int | None = None) -> List[Venta]:
    if pesos is None:
        pesos = [40, 25, 15, 12, 8]
    if seed is not None:
        random.seed(seed)
    nombres = productos
    choices = random.choices(nombres, weights=pesos, k=n)
    ventas = []
    for prod in choices:
        cantidad = random.randint(1, 5)
        ventas.append(Venta(prod, cantidad))
    return ventas
