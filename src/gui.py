"""gui.py
Interfaz gráfica para el Sistema de Ventas.

Al abrir la app, carga automáticamente el CSV.
Incluye gráficas con matplotlib incrustadas en tkinter.

Para ejecutar:
    python gui.py
(desde la carpeta src/)
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")                          # backend para tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from sistema_ventas import SistemaDeVentas
from producto import Producto
from venta import Venta
from analizador import Analizador


# ─── Colores ────────────────────────────────────────────────────
COLOR_FONDO      = "#F5F0EB"   # beige claro
COLOR_PANEL      = "#FFFFFF"   # blanco
COLOR_PRIMARIO   = "#4A6FA5"   # azul suave
COLOR_SECUNDARIO = "#6B9080"   # verde salvia
COLOR_ACENTO     = "#E07A5F"   # terracota
COLOR_TEXTO      = "#2D3436"   # gris oscuro

FUENTE_TITULO    = ("Segoe UI", 16, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 12, "bold")
FUENTE_NORMAL    = ("Segoe UI", 10)

# Ruta al CSV (sube un nivel desde src/ hasta la carpeta del proyecto)
RUTA_CSV = os.path.join(os.path.dirname(__file__), "..", "datos", "Ventas.csv")


class AplicacionVentas:
    """Ventana principal. Carga datos al iniciar y muestra el sistema."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistema de Análisis de Ventas")
        self.root.geometry("950x650")
        self.root.configure(bg=COLOR_FONDO)
        self.root.minsize(800, 550)

        # Instancia del sistema (igual que en main.py)
        self.sistema = SistemaDeVentas()

        self._crear_interfaz()

        # ── Cargar CSV automáticamente al abrir ──
        self._cargar_datos_al_inicio()

    # ─── Interfaz ────────────────────────────────────────────────

    def _crear_interfaz(self):
        """Construye todos los widgets."""

        # Encabezado azul
        encabezado = tk.Frame(self.root, bg=COLOR_PRIMARIO, height=60)
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)
        tk.Label(encabezado, text="📊 Sistema de Análisis de Ventas",
                 font=FUENTE_TITULO, bg=COLOR_PRIMARIO, fg="white").pack(expand=True)

        # Contenedor principal
        contenedor = tk.Frame(self.root, bg=COLOR_FONDO)
        contenedor.pack(fill="both", expand=True, padx=15, pady=15)

        # ── Panel menú lateral ──
        panel_menu = tk.Frame(contenedor, bg=COLOR_PANEL, width=200,
                              highlightbackground="#DDD", highlightthickness=1)
        panel_menu.pack(side="left", fill="y", padx=(0, 10))
        panel_menu.pack_propagate(False)

        tk.Label(panel_menu, text="Menú", font=FUENTE_SUBTITULO,
                 bg=COLOR_PANEL, fg=COLOR_TEXTO).pack(pady=(15, 10))

        botones = [
            ("Listar productos",  self._listar_productos,  COLOR_PRIMARIO),
            ("Listar ventas",     self._listar_ventas,     COLOR_PRIMARIO),
            ("Ver métricas",      self._ver_metricas,      COLOR_ACENTO),
            ("Gráfica categorías", self._grafica_categorias, COLOR_SECUNDARIO),
            ("Gráfica temporadas", self._grafica_temporadas, COLOR_SECUNDARIO),
            ("Gráfica productos",  self._grafica_productos,  COLOR_SECUNDARIO),
        ]

        for texto, comando, color in botones:
            tk.Button(panel_menu, text=texto, command=comando,
                      font=FUENTE_NORMAL, bg=color, fg="white",
                      activebackground=color, activeforeground="white",
                      relief="flat", cursor="hand2", width=22, pady=7
                      ).pack(pady=4, padx=10)

        tk.Button(panel_menu, text="Salir", command=self.root.quit,
                  font=FUENTE_NORMAL, bg="#B2675E", fg="white",
                  activebackground="#944E47", activeforeground="white",
                  relief="flat", cursor="hand2", width=22, pady=7
                  ).pack(side="bottom", pady=15, padx=10)

        # ── Panel de contenido (texto + gráficas) ──
        self.panel_contenido = tk.Frame(contenedor, bg=COLOR_PANEL,
                                        highlightbackground="#DDD", highlightthickness=1)
        self.panel_contenido.pack(side="left", fill="both", expand=True)

        # Área de texto con scroll
        self.texto_resultado = tk.Text(
            self.panel_contenido, font=FUENTE_NORMAL,
            bg=COLOR_PANEL, fg=COLOR_TEXTO,
            relief="flat", wrap="word", padx=15, pady=15,
            state="disabled"
        )
        scrollbar = ttk.Scrollbar(self.panel_contenido,
                                  command=self.texto_resultado.yview)
        self.texto_resultado.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.texto_resultado.pack(fill="both", expand=True)

    # ─── Helpers de texto ────────────────────────────────────────

    def _mostrar_texto(self, texto: str):
        """Reemplaza el contenido del área de texto."""
        self._limpiar_grafica()
        self.texto_resultado.pack(fill="both", expand=True)
        self.texto_resultado.config(state="normal")
        self.texto_resultado.delete("1.0", "end")
        self.texto_resultado.insert("end", texto)
        self.texto_resultado.config(state="disabled")

    def _limpiar_grafica(self):
        """Elimina cualquier gráfica que esté visible."""
        for widget in self.panel_contenido.winfo_children():
            if isinstance(widget, tk.Frame):  # el frame del canvas
                widget.destroy()

    def _mostrar_grafica(self, fig):
        """Muestra una figura de matplotlib en el panel de contenido."""
        self._limpiar_grafica()
        self.texto_resultado.pack_forget()  # ocultar el texto

        # Incrustar la figura en tkinter
        frame_canvas = tk.Frame(self.panel_contenido, bg=COLOR_PANEL)
        frame_canvas.pack(fill="both", expand=True)

        canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ─── Carga automática ─────────────────────────────────────────

    def _cargar_datos_al_inicio(self):
        """Carga el CSV automáticamente cuando se abre la app."""
        try:
            self.sistema.cargar_csv(RUTA_CSV)
            n_prods = len(self.sistema.obtener_productos())
            n_ventas = len(self.sistema.obtener_ventas())
            self._mostrar_texto(
                "✅ Datos cargados automáticamente.\n\n"
                f"   Productos distintos:  {n_prods}\n"
                f"   Registros de ventas:  {n_ventas}\n\n"
                "Usa el menú de la izquierda para explorar los datos."
            )
        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró el archivo:\n{RUTA_CSV}")
        except Exception as e:
            messagebox.showerror("Error al cargar datos", str(e))

    # ─── Opciones del menú ────────────────────────────────────────

    def _listar_productos(self):
        """Muestra el catálogo de productos."""
        productos = self.sistema.obtener_productos()
        if not productos:
            self._mostrar_texto("No hay productos registrados.")
            return
        lineas = ["📦  Catálogo de Productos\n", "-" * 50]
        for i, p in enumerate(productos, start=1):
            lineas.append(f"  {i}. {p}")
        lineas.append("-" * 50)
        lineas.append(f"\nTotal de productos distintos: {len(productos)}")
        self._mostrar_texto("\n".join(lineas))

    def _listar_ventas(self):
        """Muestra las últimas 50 ventas (el CSV tiene 3900 filas)."""
        ventas = self.sistema.obtener_ventas()
        if not ventas:
            self._mostrar_texto("No hay ventas registradas.")
            return
        lineas = [f"🧾  Ventas Registradas (mostrando las últimas 50 de {len(ventas)})\n",
                  "-" * 55]
        # Mostrar solo las últimas 50 para no saturar la pantalla
        for i, v in enumerate(ventas[-50:], start=len(ventas) - 49):
            lineas.append(f"  {i}. {v}")
        lineas.append("-" * 55)
        self._mostrar_texto("\n".join(lineas))

    def _ver_metricas(self):
        """Calcula y muestra las métricas usando el Analizador."""
        df = self.sistema.obtener_dataframe()
        if df.empty:
            self._mostrar_texto("No hay datos para analizar.")
            return

        # Crear Analizador con el DataFrame del sistema
        analizador = Analizador(df)
        resumen = analizador.resumen_general(imprimir=False)

        total = resumen["total_ventas"]
        mas = resumen["producto_mas_vendido"]
        menos = resumen["producto_menos_demandado"]
        prom = resumen["ingreso_promedio_por_venta"]
        por_cat = resumen["ventas_por_categoria"]
        por_temp = resumen["ventas_por_temporada"]
        uds_cat = resumen["unidades_por_categoria"]

        lineas = ["📈  Métricas del Negocio\n", "=" * 50,
                  f"  Total de ventas:          ${total:,.2f}",
                  f"  Ingreso promedio/venta:   ${prom:,.2f}", ""]

        if not mas.empty:
            lineas.append(f"  Producto más vendido:     {mas.index[0]} ({int(mas.iloc[0])} uds.)")
        if not menos.empty:
            lineas.append(f"  Producto menos vendido:   {menos.index[0]} ({int(menos.iloc[0])} uds.)")

        lineas += ["\n" + "=" * 50, "  📂  Ventas por Categoría", "  " + "-" * 40]
        for cat, val in por_cat.items():
            lineas.append(f"    {cat:20s}  ${val:>12,.2f}")

        lineas += ["\n  🌦️  Ventas por Temporada", "  " + "-" * 40]
        for temp, val in por_temp.items():
            lineas.append(f"    {temp:20s}  ${val:>12,.2f}")

        lineas += ["\n  📦  Unidades por Categoría", "  " + "-" * 40]
        for cat, uds in uds_cat.items():
            lineas.append(f"    {cat:20s}  {int(uds):>6} uds.")

        lineas.append("=" * 50)
        self._mostrar_texto("\n".join(lineas))

    # ─── Gráficas con matplotlib ──────────────────────────────────

    def _grafica_categorias(self):
        """Gráfica de barras: ventas totales por categoría."""
        df = self.sistema.obtener_dataframe()
        if df.empty:
            self._mostrar_texto("No hay datos para graficar.")
            return

        # Calcular con el Analizador
        analizador = Analizador(df)
        datos = analizador.ventas_por_categoria()  # pd.Series

        # Crear figura
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor(COLOR_PANEL)
        ax.set_facecolor(COLOR_PANEL)

        colores = ["#4A6FA5", "#6B9080", "#E07A5F", "#B5838D"]
        ax.bar(datos.index, datos.values, color=colores[:len(datos)])

        ax.set_title("Ventas totales por categoría", fontsize=13, pad=12)
        ax.set_xlabel("Categoría")
        ax.set_ylabel("Total ($)")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

        plt.tight_layout()
        self._mostrar_grafica(fig)

    def _grafica_temporadas(self):
        """Gráfica de torta: distribución de ventas por temporada."""
        df = self.sistema.obtener_dataframe()
        if df.empty:
            self._mostrar_texto("No hay datos para graficar.")
            return

        analizador = Analizador(df)
        datos = analizador.ventas_por_temporada()  # pd.Series

        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor(COLOR_PANEL)

        colores = ["#4A6FA5", "#6B9080", "#E07A5F", "#B5838D"]
        ax.pie(datos.values, labels=datos.index,
               autopct="%1.1f%%", colors=colores, startangle=90)
        ax.set_title("Distribución de ventas por temporada", fontsize=13, pad=12)

        plt.tight_layout()
        self._mostrar_grafica(fig)

    def _grafica_productos(self):
        """Gráfica de barras horizontales: top 10 productos por ventas."""
        df = self.sistema.obtener_dataframe()
        if df.empty:
            self._mostrar_texto("No hay datos para graficar.")
            return

        # Top 10 productos por ingreso total
        top10 = df.groupby("producto")["total"].sum().sort_values(ascending=True).tail(10)

        fig, ax = plt.subplots(figsize=(6, 4.5))
        fig.patch.set_facecolor(COLOR_PANEL)
        ax.set_facecolor(COLOR_PANEL)

        ax.barh(top10.index, top10.values, color=COLOR_PRIMARIO)
        ax.set_title("Top 10 productos por ingresos", fontsize=13, pad=12)
        ax.set_xlabel("Total ($)")
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

        plt.tight_layout()
        self._mostrar_grafica(fig)


# ─── Punto de entrada ────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionVentas(root)
    root.mainloop()
