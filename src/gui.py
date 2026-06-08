"""gui.py
Interfaz gráfica (tkinter) para el Sistema de Ventas.

Usa las mismas clases del proyecto:
  - Producto, Venta, SistemaDeVentas, Analizador.

Para ejecutar:
    python src/gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

from sistema_ventas import SistemaDeVentas
from producto import Producto
from venta import Venta
from analizador import Analizador


# ─── Paleta de colores ───────────────────────────────────────────
COLOR_FONDO       = "#F5F0EB"   # beige claro
COLOR_PANEL       = "#FFFFFF"   # blanco
COLOR_PRIMARIO    = "#4A6FA5"   # azul suave
COLOR_SECUNDARIO  = "#6B9080"   # verde salvia
COLOR_ACENTO      = "#E07A5F"   # terracota suave
COLOR_TEXTO       = "#2D3436"   # gris oscuro
COLOR_TEXTO_CLARO = "#636E72"   # gris medio
FUENTE_TITULO     = ("Segoe UI", 16, "bold")
FUENTE_SUBTITULO  = ("Segoe UI", 12, "bold")
FUENTE_NORMAL     = ("Segoe UI", 10)
FUENTE_PEQUENA    = ("Segoe UI", 9)

# Ruta al CSV (relativa a la ubicación del script)
RUTA_CSV = os.path.join(os.path.dirname(__file__), "..", "datos", "ventas_tienda.csv")


class AplicacionVentas:
    """Ventana principal de la aplicación."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistema de Análisis de Ventas")
        self.root.geometry("900x620")
        self.root.configure(bg=COLOR_FONDO)
        self.root.minsize(800, 550)

        # ── Instancia del sistema (igual que en main.py) ──
        self.sistema = SistemaDeVentas()

        self._crear_interfaz()

    # ─── Construcción de la interfaz ──────────────────────────────

    def _crear_interfaz(self):
        """Crea todos los widgets de la ventana."""

        # ── Encabezado ──
        encabezado = tk.Frame(self.root, bg=COLOR_PRIMARIO, height=60)
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)

        tk.Label(
            encabezado,
            text="📊 Sistema de Análisis de Ventas",
            font=FUENTE_TITULO,
            bg=COLOR_PRIMARIO,
            fg="white",
        ).pack(expand=True)

        # ── Contenedor principal (botones a la izquierda, contenido a la derecha) ──
        contenedor = tk.Frame(self.root, bg=COLOR_FONDO)
        contenedor.pack(fill="both", expand=True, padx=15, pady=15)

        # Panel de botones (menú lateral)
        panel_menu = tk.Frame(contenedor, bg=COLOR_PANEL, width=220,
                              highlightbackground="#DDD", highlightthickness=1)
        panel_menu.pack(side="left", fill="y", padx=(0, 10))
        panel_menu.pack_propagate(False)

        tk.Label(
            panel_menu, text="Menú", font=FUENTE_SUBTITULO,
            bg=COLOR_PANEL, fg=COLOR_TEXTO
        ).pack(pady=(15, 10))

        # Lista de botones: (texto, comando, color)
        botones = [
            ("Cargar datos CSV",        self._cargar_csv,         COLOR_SECUNDARIO),
            ("Registrar producto",      self._registrar_producto, COLOR_PRIMARIO),
            ("Registrar venta",         self._registrar_venta,    COLOR_PRIMARIO),
            ("Listar productos",        self._listar_productos,   COLOR_PRIMARIO),
            ("Listar ventas",           self._listar_ventas,      COLOR_PRIMARIO),
            ("Ver métricas",            self._ver_metricas,       COLOR_ACENTO),
        ]

        for texto, comando, color in botones:
            btn = tk.Button(
                panel_menu,
                text=texto,
                command=comando,
                font=FUENTE_NORMAL,
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                width=22,
                pady=7,
            )
            btn.pack(pady=4, padx=10)

        # Botón de salir al final
        tk.Button(
            panel_menu,
            text="Salir",
            command=self.root.quit,
            font=FUENTE_NORMAL,
            bg="#B2675E",
            fg="white",
            activebackground="#944E47",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            width=22,
            pady=7,
        ).pack(side="bottom", pady=15, padx=10)

        # Panel de contenido (área derecha)
        self.panel_contenido = tk.Frame(
            contenedor, bg=COLOR_PANEL,
            highlightbackground="#DDD", highlightthickness=1
        )
        self.panel_contenido.pack(side="left", fill="both", expand=True)

        # Área de texto con scroll para mostrar resultados
        self.texto_resultado = tk.Text(
            self.panel_contenido,
            font=FUENTE_NORMAL,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            relief="flat",
            wrap="word",
            padx=15,
            pady=15,
            state="disabled",         # solo lectura por defecto
        )
        scrollbar = ttk.Scrollbar(self.panel_contenido,
                                  command=self.texto_resultado.yview)
        self.texto_resultado.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.texto_resultado.pack(fill="both", expand=True)

        # Mensaje de bienvenida
        self._mostrar_texto(
            "¡Bienvenido al Sistema de Ventas!\n\n"
            "Usa el menú de la izquierda para comenzar.\n\n"
            "• Carga los datos del CSV para analizar ventas.\n"
            "• O registra productos y ventas manualmente.\n"
            "• Luego consulta las métricas del negocio."
        )

    # ─── Helpers para mostrar texto ──────────────────────────────

    def _mostrar_texto(self, texto: str):
        """Reemplaza el contenido del área de texto."""
        self.texto_resultado.config(state="normal")
        self.texto_resultado.delete("1.0", "end")
        self.texto_resultado.insert("end", texto)
        self.texto_resultado.config(state="disabled")

    def _agregar_texto(self, texto: str):
        """Agrega texto al final del área de texto."""
        self.texto_resultado.config(state="normal")
        self.texto_resultado.insert("end", texto)
        self.texto_resultado.config(state="disabled")

    # ─── Funciones del menú ──────────────────────────────────────

    def _cargar_csv(self):
        """Carga datos desde el archivo CSV (opción 1 del menú)."""
        try:
            self.sistema.cargar_csv(RUTA_CSV)
            prods = len(self.sistema.obtener_productos())
            vtas = len(self.sistema.obtener_ventas())
            self._mostrar_texto(
                f"✅ Datos cargados desde CSV correctamente.\n\n"
                f"   Productos en catálogo: {prods}\n"
                f"   Ventas registradas:    {vtas}"
            )
        except FileNotFoundError:
            messagebox.showerror("Error",
                                 f"No se encontró el archivo:\n{RUTA_CSV}")
        except Exception as e:
            messagebox.showerror("Error al cargar CSV", str(e))

    def _registrar_producto(self):
        """Registrar un producto manualmente (opción 2)."""
        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar producto")
        ventana.geometry("350x260")
        ventana.configure(bg=COLOR_PANEL)
        ventana.resizable(False, False)
        ventana.grab_set()

        tk.Label(ventana, text="Nombre del producto:", font=FUENTE_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(20, 5))
        entrada_nombre = tk.Entry(ventana, font=FUENTE_NORMAL, width=25)
        entrada_nombre.pack()

        tk.Label(ventana, text="Precio unitario:", font=FUENTE_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(10, 5))
        entrada_precio = tk.Entry(ventana, font=FUENTE_NORMAL, width=25)
        entrada_precio.pack()

        tk.Label(ventana, text="Categoría:", font=FUENTE_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(10, 5))
        entrada_cat = tk.Entry(ventana, font=FUENTE_NORMAL, width=25)
        entrada_cat.insert(0, "General")
        entrada_cat.pack()

        def confirmar():
            nombre = entrada_nombre.get().strip()
            categoria = entrada_cat.get().strip() or "General"
            try:
                precio = float(entrada_precio.get().strip())
            except ValueError:
                messagebox.showerror("Error", "El precio debe ser un número válido.")
                return
            try:
                p = Producto(nombre, precio, categoria)
                agregado = self.sistema.registrar_producto(p)
                if agregado:
                    self._mostrar_texto(f"✅ Producto registrado: {p}")
                else:
                    self._mostrar_texto("⚠️ El producto ya existe en el catálogo.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
            ventana.destroy()

        tk.Button(ventana, text="Registrar", command=confirmar,
                  font=FUENTE_NORMAL, bg=COLOR_PRIMARIO, fg="white",
                  relief="flat", cursor="hand2", padx=20, pady=5
                  ).pack(pady=15)

    def _registrar_venta(self):
        """Registrar una venta manualmente (opción 3)."""
        productos = self.sistema.obtener_productos()
        if not productos:
            messagebox.showinfo("Sin productos",
                                "No hay productos registrados.\n"
                                "Carga el CSV o agrega productos primero.")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar venta")
        ventana.geometry("400x320")
        ventana.configure(bg=COLOR_PANEL)
        ventana.resizable(False, False)
        ventana.grab_set()

        tk.Label(ventana, text="Selecciona un producto:", font=FUENTE_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(20, 5))

        # Combobox con los productos
        nombres = [f"{p.get_nombre()} — ${p.get_precio_unitario():,.2f}"
                   for p in productos]
        combo = ttk.Combobox(ventana, values=nombres, state="readonly",
                             font=FUENTE_NORMAL, width=30)
        combo.current(0)
        combo.pack()

        tk.Label(ventana, text="Cantidad:", font=FUENTE_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(15, 5))
        entrada_cant = tk.Entry(ventana, font=FUENTE_NORMAL, width=15, justify="center")
        entrada_cant.pack()

        tk.Label(ventana, text="Tienda:", font=FUENTE_NORMAL,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(10, 5))
        entrada_tienda = tk.Entry(ventana, font=FUENTE_NORMAL, width=25)
        entrada_tienda.insert(0, "General")
        entrada_tienda.pack()

        def confirmar():
            idx = combo.current()
            tienda = entrada_tienda.get().strip() or "General"
            try:
                cantidad = int(entrada_cant.get().strip())
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número entero.")
                return
            try:
                v = Venta(productos[idx], cantidad, tienda)
                self.sistema.registrar_venta(v)
                self._mostrar_texto(f"✅ Venta registrada: {v}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
            ventana.destroy()

        tk.Button(ventana, text="Registrar venta", command=confirmar,
                  font=FUENTE_NORMAL, bg=COLOR_PRIMARIO, fg="white",
                  relief="flat", cursor="hand2", padx=20, pady=5
                  ).pack(pady=20)

    def _listar_productos(self):
        """Muestra todos los productos registrados (opción 4)."""
        productos = self.sistema.obtener_productos()
        if not productos:
            self._mostrar_texto("No hay productos registrados.")
            return
        lineas = ["📦  Catálogo de Productos\n"]
        lineas.append("-" * 45)
        for i, p in enumerate(productos, start=1):
            lineas.append(f"  {i}. {p}")
        lineas.append("-" * 45)
        lineas.append(f"\nTotal de productos: {len(productos)}")
        self._mostrar_texto("\n".join(lineas))

    def _listar_ventas(self):
        """Muestra todas las ventas registradas (opción 5)."""
        ventas = self.sistema.obtener_ventas()
        if not ventas:
            self._mostrar_texto("No hay ventas registradas.")
            return
        lineas = ["🧾  Ventas Registradas\n"]
        lineas.append("-" * 50)
        for i, v in enumerate(ventas, start=1):
            lineas.append(f"  {i}. {v}")
        lineas.append("-" * 50)
        lineas.append(f"\nTotal de ventas: {len(ventas)}")
        self._mostrar_texto("\n".join(lineas))

    def _ver_metricas(self):
        """Muestra las métricas del Analizador (opción 6)."""
        df = self.sistema.obtener_dataframe()
        if df.empty:
            self._mostrar_texto("No hay ventas registradas para analizar.")
            return

        analizador = Analizador(df)
        resumen = analizador.resumen_general(imprimir=False)

        total = resumen["total_ventas"]
        mas = resumen["producto_mas_vendido"]
        menos = resumen["producto_menos_demandado"]
        prom_venta = resumen["ingreso_promedio_por_venta"]
        prom_prod = resumen["ingreso_promedio_por_producto"]
        por_cat = resumen["ventas_por_categoria"]
        por_tienda = resumen["ventas_por_tienda"]
        uds_cat = resumen["unidades_por_categoria"]

        lineas = ["📈  Métricas del Negocio\n"]
        lineas.append("=" * 50)

        # ── Métricas generales ──
        lineas.append(f"  Total de ventas:           ${total:,.2f}")
        lineas.append("")
        if not mas.empty:
            lineas.append(f"  Producto más vendido:      {mas.index[0]}"
                          f"  ({int(mas.iloc[0])} uds.)")
        if not menos.empty:
            lineas.append(f"  Producto menos demandado:  {menos.index[0]}"
                          f"  ({int(menos.iloc[0])} uds.)")
        lineas.append("")
        lineas.append(f"  Ingreso promedio / venta:  ${prom_venta:,.2f}")

        # ── Ventas por categoría ──
        lineas.append("\n" + "=" * 50)
        lineas.append("  📂  Ventas por Categoría")
        lineas.append("  " + "-" * 40)
        for cat, valor in por_cat.items():
            lineas.append(f"    {cat:22s}  ${valor:>14,.2f}")

        # ── Unidades por categoría ──
        lineas.append("\n  📦  Unidades por Categoría")
        lineas.append("  " + "-" * 40)
        for cat, uds in uds_cat.items():
            lineas.append(f"    {cat:22s}  {int(uds):>8} uds.")

        # ── Ventas por tienda ──
        lineas.append("\n" + "=" * 50)
        lineas.append("  🏪  Ventas por Tienda")
        lineas.append("  " + "-" * 40)
        for tienda, valor in por_tienda.items():
            lineas.append(f"    {tienda:22s}  ${valor:>14,.2f}")

        # ── Ingreso promedio por producto ──
        lineas.append("\n" + "=" * 50)
        lineas.append("  💰  Ingreso Promedio por Producto")
        lineas.append("  " + "-" * 40)
        for nombre, valor in prom_prod.items():
            lineas.append(f"    {nombre:22s}  ${valor:>14,.2f}")
        lineas.append("=" * 50)

        self._mostrar_texto("\n".join(lineas))


# ─── Punto de entrada ────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionVentas(root)
    root.mainloop()
