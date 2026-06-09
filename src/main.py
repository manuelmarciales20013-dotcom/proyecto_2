"""main.py
Menú interactivo por consola para el Sistema de Ventas.
"""
import os
from sistema_ventas import SistemaDeVentas
from producto import Producto
from venta import Venta
from analizador import Analizador


# Ruta al CSV (sube un nivel desde src/)
RUTA_CSV = os.path.join(os.path.dirname(__file__), "..", "datos", "Ventas.csv")


def _input_int(prompt: str, default: int | None = None) -> int:
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            return int(val)
        except ValueError:
            print("Ingrese un número entero válido.")


def _input_float(prompt: str) -> float:
    while True:
        val = input(prompt).strip()
        try:
            return float(val)
        except ValueError:
            print("Ingrese un número válido (ej. 25000)")


def menu() -> None:
    sistema = SistemaDeVentas()
    while True:
        print("\n--- Sistema de Ventas — Menú ---")
        print("1) Cargar datos desde CSV")
        print("2) Registrar producto (manual)")
        print("3) Registrar venta (manual)")
        print("4) Listar productos")
        print("5) Listar ventas")
        print("6) Ver métricas")
        print("7) Salir")
        opt = input("Selecciona una opción: ").strip()

        if opt == "1":
            sistema.cargar_csv(RUTA_CSV)
            print(f"Cargados {len(sistema.obtener_productos())} productos "
                  f"y {len(sistema.obtener_ventas())} ventas.")

        elif opt == "2":
            nombre = input("Nombre del producto: ").strip()
            precio = _input_float("Precio unitario: ")
            categoria = input("Categoría: ").strip() or "General"
            try:
                p = Producto(nombre, precio, categoria)
                agregado = sistema.registrar_producto(p)
                print("Producto registrado." if agregado else "El producto ya existe.")
            except Exception as e:
                print("Error al crear producto:", e)

        elif opt == "3":
            productos = sistema.obtener_productos()
            if not productos:
                print("No hay productos. Carga el CSV primero o registra productos.")
                continue
            print("Catálogo:")
            for i, p in enumerate(productos, start=1):
                print(f"{i}) {p.get_nombre()} — ${p.get_precio_unitario():,.2f}")
            idx = _input_int("Selecciona producto (número): ")
            if idx < 1 or idx > len(productos):
                print("Selección inválida.")
                continue
            cantidad = _input_int("Cantidad: ")
            temporada = input("Temporada (Spring/Summer/Fall/Winter): ").strip() or "General"
            try:
                v = Venta(productos[idx - 1], cantidad, temporada)
                sistema.registrar_venta(v)
                print("Venta registrada.")
            except Exception as e:
                print("Error al registrar venta:", e)

        elif opt == "4":
            sistema.listar_productos()

        elif opt == "5":
            sistema.listar_ventas()

        elif opt == "6":
            df = sistema.obtener_dataframe()
            if df.empty:
                print("No hay ventas registradas.")
                continue
            analizador = Analizador(df)
            analizador.resumen_general()

        elif opt == "7":
            print("Saliendo...")
            break

        else:
            print("Opción no válida.")


if __name__ == "__main__":
    menu()
