"""main.py
Menú interactivo para el sistema de ventas.
"""
from sistema_ventas import SistemaDeVentas
from producto import Producto
from venta import Venta
from analizador import Analizador


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
            sistema.cargar_csv("datos/ventas_tienda.csv")
            print(f"Cargados {len(sistema.obtener_productos())} productos y {len(sistema.obtener_ventas())} ventas.")

        elif opt == "2":
            nombre = input("Nombre del producto: ").strip()
            precio = _input_float("Precio unitario: ")
            try:
                p = Producto(nombre, precio)
                added = sistema.registrar_producto(p)
                print("Producto registrado." if added else "El producto ya existe en el catálogo.")
            except Exception as e:
                print("Error al crear producto:", e)

        elif opt == "3":
            productos = sistema.obtener_productos()
            if not productos:
                print("No hay productos registrados. Agrega productos primero o carga datos desde CSV.")
                continue
            print("Catálogo:")
            for i, p in enumerate(productos, start=1):
                print(f"{i}) {p.get_nombre()} — ${p.get_precio_unitario():,.2f}")
            idx = _input_int("Selecciona producto (número): ")
            if idx < 1 or idx > len(productos):
                print("Selección inválida.")
                continue
            cantidad = _input_int("Cantidad: ")
            try:
                v = Venta(productos[idx - 1], cantidad)
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
