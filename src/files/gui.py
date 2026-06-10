"""gui.py  ──  Sistema de Análisis de Ventas  ──  v2.0
Interfaz rediseñada con ttk.Notebook:
  · Pestaña 1 — Dashboard (KPI cards + gráficas resumen)
  · Pestaña 2 — Tabla interactiva con filtros
  · Pestaña 3 — Galería de gráficas (9 charts)
  · Pestaña 4 — Análisis avanzado (demográfico + correlaciones)
  · Pestaña 5 — Exportar reportes
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd

from sistema_ventas import SistemaDeVentas
from analizador import Analizador
from exportador import exportar_csv, exportar_txt, exportar_grafica_png

# ═══════════════════════════════════════════════════════════════
# PALETA Y TIPOGRAFÍA  ·  Light Blue (Power BI style)
# ═══════════════════════════════════════════════════════════════
BG          = "#F5F9FD"   # fondo blanco azulado
PANEL       = "#DDEAF6"   # panel azul pálido
CARD        = "#EBF3FA"   # card azul muy claro
BORDER      = "#BDD7EE"   # borde azul suave
ACCENT1     = "#1F4E79"   # azul marino oscuro — principal
ACCENT2     = "#2E75B6"   # azul medio
ACCENT3     = "#4472C4"   # azul royal
ACCENT4     = "#ED7D31"   # naranja — alertas / contraste
ACCENT5     = "#5B9BD5"   # azul claro
TXT_MAIN    = "#172B4D"   # texto principal oscuro
TXT_SUB     = "#2E5A8A"   # texto azul secundario
TXT_MUTED   = "#7BA7C9"   # texto muted grisáceo

PALETTE     = ["#2E75B6", "#1F4E79", "#4472C4", "#9DC3E6", "#5B9BD5",
               "#BDD7EE", "#172B4D", "#70B0D9", "#A8C8E5", "#DDEBF7"]

F_TITLE     = ("Segoe UI", 15, "bold")
F_SUBTITLE  = ("Segoe UI", 11, "bold")
F_BODY      = ("Segoe UI", 10)
F_SMALL     = ("Segoe UI", 9)
F_KPI       = ("Segoe UI", 22, "bold")
F_KPI_LABEL = ("Segoe UI", 9)

RUTA_CSV = r"C:\Users\Jhan\Documents\ProyectoProgramacionVentas\proyecto_2\datos\Ventas.csv"


# ═══════════════════════════════════════════════════════════════
# HELPERS MATPLOTLIB
# ═══════════════════════════════════════════════════════════════

def _apply_dark_style(ax, fig):
    fig.patch.set_facecolor(PANEL)
    ax.set_facecolor(CARD)
    ax.tick_params(colors=TXT_SUB, labelsize=8)
    ax.xaxis.label.set_color(TXT_SUB)
    ax.yaxis.label.set_color(TXT_SUB)
    ax.title.set_color(TXT_MAIN)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.title.set_fontweight("bold")


def _fmt_miles(ax, axis="y"):
    fmt = plt.FuncFormatter(lambda x, _: f"${x:,.0f}")
    if axis == "y":
        ax.yaxis.set_major_formatter(fmt)
    else:
        ax.xaxis.set_major_formatter(fmt)


# ═══════════════════════════════════════════════════════════════
# APLICACIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════

class AplicacionVentas:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistema de Análisis de Ventas  v2.0")
        self.root.geometry("1180x720")
        self.root.configure(bg=BG)
        self.root.minsize(900, 600)

        self.sistema    = SistemaDeVentas()
        self.df         = pd.DataFrame()
        self.analizador = None
        self._figuras_galeria: dict = {}   # nombre → fig (para exportar)

        self._configurar_estilos()
        self._construir_interfaz()
        self._cargar_csv_inicio()

    # ── Estilos ttk ─────────────────────────────────────────────

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook",
                         background=BG, borderwidth=0, tabmargins=[4, 4, 0, 0])
        style.configure("TNotebook.Tab",
                         background=PANEL, foreground=TXT_SUB,
                         font=F_BODY, padding=[14, 7], borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", CARD), ("active", BORDER)],
                  foreground=[("selected", ACCENT1), ("active", TXT_MAIN)])

        style.configure("Treeview",
                         background=CARD, foreground=TXT_MAIN,
                         fieldbackground=CARD, rowheight=24,
                         borderwidth=0, font=F_SMALL)
        style.configure("Treeview.Heading",
                         background=PANEL, foreground=ACCENT2,
                         font=("Segoe UI", 9, "bold"), borderwidth=0)
        style.map("Treeview",
                  background=[("selected", ACCENT2)],
                  foreground=[("selected", BG)])

        style.configure("TScrollbar",
                         background=BORDER, troughcolor=PANEL,
                         borderwidth=0, arrowcolor=TXT_SUB)
        style.configure("TCombobox",
                         background=CARD, foreground=TXT_MAIN,
                         fieldbackground=CARD, selectbackground=ACCENT2,
                         font=F_SMALL)
        style.configure("TEntry",
                         background=CARD, foreground=TXT_MAIN,
                         insertcolor=TXT_MAIN, fieldbackground=CARD,
                         font=F_SMALL)

    # ── Esqueleto principal ──────────────────────────────────────

    def _construir_interfaz(self):
        # Header
        hdr = tk.Frame(self.root, bg=PANEL, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="◈  SALES INTELLIGENCE DASHBOARD",
                 font=("Segoe UI", 13, "bold"),
                 bg=PANEL, fg=ACCENT1).pack(side="left", padx=20)
        self._lbl_estado = tk.Label(hdr, text="Cargando…",
                                     font=F_SMALL, bg=PANEL, fg=TXT_SUB)
        self._lbl_estado.pack(side="right", padx=20)

        # Notebook
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        self._construir_tab_dashboard()
        self._construir_tab_tabla()
        self._construir_tab_galeria()
        self._construir_tab_avanzado()
        self._construir_tab_exportar()

    # ════════════════════════════════════════════════════════════
    # PESTAÑA 1 — DASHBOARD
    # ════════════════════════════════════════════════════════════

    def _construir_tab_dashboard(self):
        frame = tk.Frame(self.nb, bg=BG)
        self.nb.add(frame, text="  📊 Dashboard  ")

        # Fila de KPIs
        self._frame_kpis = tk.Frame(frame, bg=BG)
        self._frame_kpis.pack(fill="x", padx=12, pady=(10, 6))

        self._kpi_vars = {}
        kpis = [
            ("total_ventas",    "Total Ingresos",   ACCENT1),
            ("n_ventas",        "Transacciones",    ACCENT2),
            ("ticket_prom",     "Ticket Promedio",  ACCENT3),
            ("n_productos",     "Productos únicos", ACCENT4),
            ("calif_prom",      "Rating Promedio",  ACCENT5),
        ]
        for key, label, color in kpis:
            card = tk.Frame(self._frame_kpis, bg=CARD,
                            highlightbackground=color,
                            highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=4)
            var = tk.StringVar(value="—")
            self._kpi_vars[key] = var
            tk.Label(card, textvariable=var,
                     font=F_KPI, bg=CARD, fg=color).pack(pady=(10, 0))
            tk.Label(card, text=label,
                     font=F_KPI_LABEL, bg=CARD, fg=TXT_SUB).pack(pady=(0, 10))

        # Dos gráficas lado a lado: categorías + temporadas
        self._frame_dash_charts = tk.Frame(frame, bg=BG)
        self._frame_dash_charts.pack(fill="both", expand=True, padx=12, pady=4)

        self._canvas_dash_izq = None
        self._canvas_dash_der = None

    def _actualizar_dashboard(self):
        if self.analizador is None or self.df.empty:
            return

        stats = self.analizador.estadisticas_precio()
        mas   = self.analizador.producto_mas_vendido()
        calif = self.analizador.calificacion_promedio_por_categoria()

        self._kpi_vars["total_ventas"].set(f"${stats['total']:,.0f}")
        self._kpi_vars["n_ventas"].set(f"{stats['n']:,}")
        self._kpi_vars["ticket_prom"].set(f"${stats['media']:,.2f}")
        self._kpi_vars["n_productos"].set(str(len(self.sistema.obtener_productos())))
        prom_calif = float(self.df["calificacion"][self.df["calificacion"] > 0].mean()) if self._tiene("calificacion") else 0
        self._kpi_vars["calif_prom"].set(f"{'★'*round(prom_calif)} {prom_calif:.1f}" if prom_calif else "—")

        # Limpiar gráficas anteriores
        for w in self._frame_dash_charts.winfo_children():
            w.destroy()
        plt.close("all")

        # Gráfica izquierda: barras por categoría
        fig1, ax1 = plt.subplots(figsize=(4.8, 3.2))
        _apply_dark_style(ax1, fig1)
        datos_cat = self.analizador.ventas_por_categoria()
        bars = ax1.bar(datos_cat.index, datos_cat.values,
                       color=PALETTE[:len(datos_cat)], width=0.6, zorder=3)
        ax1.set_title("Ingresos por categoría", fontsize=10, pad=8)
        ax1.set_xlabel("")
        _fmt_miles(ax1)
        ax1.grid(axis="y", color=BORDER, linestyle="--", alpha=0.5, zorder=0)
        ax1.tick_params(axis="x", rotation=15)
        plt.tight_layout()
        self._incrustar_figura(fig1, self._frame_dash_charts, side="left")

        # Gráfica derecha: pie de temporadas
        fig2, ax2 = plt.subplots(figsize=(4.0, 3.2))
        fig2.patch.set_facecolor(PANEL)
        datos_temp = self.analizador.ventas_por_temporada()
        wedges, texts, autotexts = ax2.pie(
            datos_temp.values,
            labels=datos_temp.index,
            autopct="%1.1f%%",
            colors=PALETTE[:len(datos_temp)],
            startangle=90,
            wedgeprops=dict(linewidth=1.5, edgecolor=PANEL),
        )
        for t in texts:
            t.set_color(TXT_SUB)
            t.set_fontsize(8)
        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(8)
            at.set_fontweight("bold")
        ax2.set_title("Distribución por temporada", fontsize=10, color=TXT_MAIN, pad=8)
        plt.tight_layout()
        self._incrustar_figura(fig2, self._frame_dash_charts, side="left")

        # Gráfica centro: top 5 productos
        fig3, ax3 = plt.subplots(figsize=(4.8, 3.2))
        _apply_dark_style(ax3, fig3)
        top5 = self.analizador.top_productos_ingreso(5).sort_values()
        ax3.barh(top5.index, top5.values, color=ACCENT2, height=0.6, zorder=3)
        ax3.set_title("Top 5 productos", fontsize=10, pad=8)
        _fmt_miles(ax3, axis="x")
        ax3.grid(axis="x", color=BORDER, linestyle="--", alpha=0.5, zorder=0)
        plt.tight_layout()
        self._incrustar_figura(fig3, self._frame_dash_charts, side="left")

    # ════════════════════════════════════════════════════════════
    # PESTAÑA 2 — TABLA INTERACTIVA
    # ════════════════════════════════════════════════════════════

    def _construir_tab_tabla(self):
        frame = tk.Frame(self.nb, bg=BG)
        self.nb.add(frame, text="  📋 Tabla  ")

        # Barra de filtros
        bar = tk.Frame(frame, bg=PANEL, pady=6)
        bar.pack(fill="x")

        tk.Label(bar, text="Buscar:", font=F_SMALL, bg=PANEL, fg=TXT_SUB).pack(side="left", padx=(12, 4))
        self._var_buscar = tk.StringVar()
        self._var_buscar.trace_add("write", lambda *_: self._filtrar_tabla())
        ttk.Entry(bar, textvariable=self._var_buscar, width=22).pack(side="left", padx=4)

        tk.Label(bar, text="Categoría:", font=F_SMALL, bg=PANEL, fg=TXT_SUB).pack(side="left", padx=(12, 4))
        self._var_cat_filtro = tk.StringVar(value="Todas")
        self._combo_cat = ttk.Combobox(bar, textvariable=self._var_cat_filtro,
                                        state="readonly", width=16)
        self._combo_cat.pack(side="left", padx=4)
        self._combo_cat.bind("<<ComboboxSelected>>", lambda _: self._filtrar_tabla())

        tk.Label(bar, text="Temporada:", font=F_SMALL, bg=PANEL, fg=TXT_SUB).pack(side="left", padx=(12, 4))
        self._var_temp_filtro = tk.StringVar(value="Todas")
        self._combo_temp = ttk.Combobox(bar, textvariable=self._var_temp_filtro,
                                         state="readonly", width=14)
        self._combo_temp.pack(side="left", padx=4)
        self._combo_temp.bind("<<ComboboxSelected>>", lambda _: self._filtrar_tabla())

        tk.Label(bar, text="Género:", font=F_SMALL, bg=PANEL, fg=TXT_SUB).pack(side="left", padx=(12, 4))
        self._var_gen_filtro = tk.StringVar(value="Todos")
        self._combo_gen = ttk.Combobox(bar, textvariable=self._var_gen_filtro,
                                        state="readonly", width=10)
        self._combo_gen.pack(side="left", padx=4)
        self._combo_gen.bind("<<ComboboxSelected>>", lambda _: self._filtrar_tabla())

        self._lbl_conteo = tk.Label(bar, text="", font=F_SMALL, bg=PANEL, fg=TXT_SUB)
        self._lbl_conteo.pack(side="right", padx=16)

        # Treeview
        cols = ["producto", "categoria", "total", "cantidad", "temporada",
                "genero", "edad", "ubicacion", "metodo_pago", "calificacion",
                "color", "talla", "frecuencia_compra"]
        headers = ["Producto", "Categoría", "Total($)", "Cant.", "Temporada",
                   "Género", "Edad", "Ubicación", "Pago", "Rating",
                   "Color", "Talla", "Frecuencia"]
        widths  = [130, 90, 80, 50, 90, 70, 50, 110, 100, 60, 80, 60, 100]

        tree_frame = tk.Frame(frame, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=6)

        scrolly = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollx = ttk.Scrollbar(tree_frame, orient="horizontal")

        self._tree = ttk.Treeview(tree_frame,
                                   columns=cols,
                                   show="headings",
                                   yscrollcommand=scrolly.set,
                                   xscrollcommand=scrollx.set,
                                   selectmode="browse")
        scrolly.config(command=self._tree.yview)
        scrollx.config(command=self._tree.xview)

        for col, hdr, w in zip(cols, headers, widths):
            self._tree.heading(col, text=hdr,
                               command=lambda c=col: self._ordenar_tabla(c))
            self._tree.column(col, width=w, minwidth=40, anchor="w")

        # Alternar color de filas
        self._tree.tag_configure("par",   background=CARD)
        self._tree.tag_configure("impar", background="#F0F7FD")

        scrolly.pack(side="right", fill="y")
        scrollx.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)

        self._df_filtrado = pd.DataFrame()
        self._orden_asc   = {}

    def _poblar_combos_tabla(self):
        if self.df.empty:
            return
        cats  = ["Todas"] + sorted(self.df["categoria"].dropna().unique().tolist())
        temps = ["Todas"] + sorted(self.df["temporada"].dropna().unique().tolist())
        gens  = ["Todos"] + sorted(self.df["genero"].dropna().unique().tolist()) if self._tiene("genero") else ["Todos"]
        self._combo_cat["values"]  = cats
        self._combo_temp["values"] = temps
        self._combo_gen["values"]  = gens

    def _filtrar_tabla(self):
        if self.df.empty:
            return
        d = self.df.copy()
        buscar = self._var_buscar.get().strip().lower()
        if buscar:
            d = d[d["producto"].str.lower().str.contains(buscar, na=False)]
        if self._var_cat_filtro.get() != "Todas":
            d = d[d["categoria"] == self._var_cat_filtro.get()]
        if self._var_temp_filtro.get() != "Todas":
            d = d[d["temporada"] == self._var_temp_filtro.get()]
        if self._tiene("genero") and self._var_gen_filtro.get() != "Todos":
            d = d[d["genero"] == self._var_gen_filtro.get()]
        self._df_filtrado = d
        self._lbl_conteo.config(text=f"{len(d):,} registros")
        self._refrescar_tree(d)

    def _refrescar_tree(self, d: pd.DataFrame):
        self._tree.delete(*self._tree.get_children())
        cols = ["producto", "categoria", "total", "cantidad", "temporada",
                "genero", "edad", "ubicacion", "metodo_pago", "calificacion",
                "color", "talla", "frecuencia_compra"]
        for i, (_, row) in enumerate(d.head(2000).iterrows()):
            vals = []
            for c in cols:
                v = row.get(c, "")
                if c == "total":
                    v = f"${float(v):,.2f}" if v != "" else ""
                elif c == "calificacion" and v:
                    try:
                        v = f"{float(v):.1f}"
                    except:
                        pass
                vals.append(str(v) if pd.notna(v) else "")
            tag = "par" if i % 2 == 0 else "impar"
            self._tree.insert("", "end", values=vals, tags=(tag,))

    def _ordenar_tabla(self, col: str):
        asc = not self._orden_asc.get(col, True)
        self._orden_asc[col] = asc
        d = self._df_filtrado if not self._df_filtrado.empty else self.df
        try:
            d = d.sort_values(col, ascending=asc)
        except Exception:
            pass
        self._refrescar_tree(d)

    # ════════════════════════════════════════════════════════════
    # PESTAÑA 3 — GALERÍA DE GRÁFICAS
    # ════════════════════════════════════════════════════════════

    def _construir_tab_galeria(self):
        frame = tk.Frame(self.nb, bg=BG)
        self.nb.add(frame, text="  📈 Gráficas  ")

        # Selector de gráfica
        sel_bar = tk.Frame(frame, bg=PANEL, pady=6)
        sel_bar.pack(fill="x")

        tk.Label(sel_bar, text="Seleccionar gráfica:", font=F_SMALL,
                 bg=PANEL, fg=TXT_SUB).pack(side="left", padx=12)

        self._graficas_disponibles = [
            ("Barras — Categorías",        self._g_barras_categorias),
            ("Torta — Temporadas",          self._g_pie_temporadas),
            ("Barras H — Top 10 productos", self._g_top10_productos),
            ("Barras — Métodos de pago",    self._g_metodos_pago),
            ("Histograma — Distribución $", self._g_histograma_precios),
            ("Scatter — Edad vs. Gasto",    self._g_scatter_edad_gasto),
            ("Boxplot — Gasto por género",  self._g_boxplot_genero),
            ("Barras agrupadas — Cat+Temp", self._g_barras_agrupadas),
            ("Barras — Tipo de envío",      self._g_envio),
        ]
        nombres = [n for n, _ in self._graficas_disponibles]
        self._var_grafica = tk.StringVar(value=nombres[0])
        combo = ttk.Combobox(sel_bar, textvariable=self._var_grafica,
                             values=nombres, state="readonly", width=36)
        combo.pack(side="left", padx=6)
        combo.bind("<<ComboboxSelected>>", lambda _: self._mostrar_grafica_seleccionada())

        tk.Button(sel_bar, text="  💾 Exportar PNG  ",
                  command=self._exportar_grafica_actual,
                  font=F_SMALL, bg=ACCENT2, fg=BG,
                  activebackground="#3A7AE0", relief="flat",
                  cursor="hand2", padx=8, pady=3).pack(side="right", padx=12)

        # Canvas de la gráfica
        self._frame_galeria_canvas = tk.Frame(frame, bg=BG)
        self._frame_galeria_canvas.pack(fill="both", expand=True)
        self._canvas_galeria  = None
        self._fig_actual      = None

    def _mostrar_grafica_seleccionada(self, *_):
        nombre = self._var_grafica.get()
        for n, fn in self._graficas_disponibles:
            if n == nombre:
                fig = fn()
                if fig:
                    self._fig_actual = fig
                    self._figuras_galeria[nombre] = fig
                    self._limpiar_frame(self._frame_galeria_canvas)
                    self._incrustar_figura(fig, self._frame_galeria_canvas,
                                           fill=True, expand=True)
                return

    # ── Las 9 gráficas ──────────────────────────────────────────

    def _g_barras_categorias(self):
        datos = self.analizador.ventas_por_categoria()
        if datos.empty:
            return None
        fig, ax = plt.subplots(figsize=(7, 4))
        _apply_dark_style(ax, fig)
        ax.bar(datos.index, datos.values, color=PALETTE[:len(datos)], width=0.6, zorder=3)
        ax.set_title("Ingresos totales por categoría", pad=10)
        ax.set_xlabel("Categoría")
        ax.set_ylabel("Total ($)")
        _fmt_miles(ax)
        ax.grid(axis="y", color=BORDER, linestyle="--", alpha=0.5, zorder=0)
        ax.tick_params(axis="x", rotation=15)
        plt.tight_layout()
        return fig

    def _g_pie_temporadas(self):
        datos = self.analizador.ventas_por_temporada()
        if datos.empty:
            return None
        fig, ax = plt.subplots(figsize=(6, 4.5))
        fig.patch.set_facecolor(PANEL)
        wedges, texts, autotexts = ax.pie(
            datos.values, labels=datos.index,
            autopct="%1.1f%%", colors=PALETTE[:len(datos)],
            startangle=90, wedgeprops=dict(linewidth=1.5, edgecolor=PANEL),
        )
        for t in texts:   t.set_color(TXT_SUB); t.set_fontsize(9)
        for at in autotexts: at.set_color("white"); at.set_fontsize(8); at.set_fontweight("bold")
        ax.set_title("Distribución de ventas por temporada", color=TXT_MAIN, pad=10)
        plt.tight_layout()
        return fig

    def _g_top10_productos(self):
        datos = self.analizador.top_productos_ingreso(10).sort_values()
        if datos.empty:
            return None
        fig, ax = plt.subplots(figsize=(7, 5))
        _apply_dark_style(ax, fig)
        bars = ax.barh(datos.index, datos.values, color=ACCENT2, height=0.65, zorder=3)
        ax.set_title("Top 10 productos por ingresos", pad=10)
        ax.set_xlabel("Total ($)")
        _fmt_miles(ax, axis="x")
        ax.grid(axis="x", color=BORDER, linestyle="--", alpha=0.5, zorder=0)
        # Etiquetas de valor
        for bar, val in zip(bars, datos.values):
            ax.text(val + datos.values.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                    f"${val:,.0f}", va="center", fontsize=7, color=TXT_SUB)
        plt.tight_layout()
        return fig

    def _g_metodos_pago(self):
        if not self._tiene("metodo_pago"):
            return None
        datos = self.analizador.ventas_por_metodo_pago()
        if datos.empty:
            return None
        fig, ax = plt.subplots(figsize=(7, 4))
        _apply_dark_style(ax, fig)
        ax.bar(datos.index, datos.values, color=PALETTE[:len(datos)], width=0.6, zorder=3)
        ax.set_title("Ingresos por método de pago", pad=10)
        _fmt_miles(ax)
        ax.grid(axis="y", color=BORDER, linestyle="--", alpha=0.5, zorder=0)
        ax.tick_params(axis="x", rotation=20)
        plt.tight_layout()
        return fig

    def _g_histograma_precios(self):
        fig, ax = plt.subplots(figsize=(7, 4))
        _apply_dark_style(ax, fig)
        vals = self.df["total"].dropna()
        n, bins, patches = ax.hist(vals, bins=30, color=ACCENT1,
                                    edgecolor=PANEL, linewidth=0.4, zorder=3)
        # Línea de media y mediana
        media   = vals.mean()
        mediana = vals.median()
        ax.axvline(media,   color=ACCENT1, linewidth=1.8, linestyle="--", label=f"Media ${media:,.0f}")
        ax.axvline(mediana, color=ACCENT4, linewidth=1.8, linestyle=":",  label=f"Mediana ${mediana:,.0f}")
        ax.legend(fontsize=8, facecolor=CARD, edgecolor=BORDER, labelcolor=TXT_MAIN)
        ax.set_title("Distribución de precios de compra", pad=10)
        ax.set_xlabel("Precio ($)")
        ax.set_ylabel("Frecuencia")
        ax.grid(axis="y", color=BORDER, linestyle="--", alpha=0.4, zorder=0)
        plt.tight_layout()
        return fig

    def _g_scatter_edad_gasto(self):
        if not self._tiene("edad"):
            return None
        sub = self.df[["edad", "total"]].dropna()
        if len(sub) < 10:
            return None
        fig, ax = plt.subplots(figsize=(7, 4))
        _apply_dark_style(ax, fig)
        # Colorear por categoría si existe
        if self._tiene("genero"):
            generos = self.df.loc[sub.index, "genero"]
            gen_uniq = generos.unique()
            colores_map = {g: PALETTE[i % len(PALETTE)] for i, g in enumerate(gen_uniq)}
            for g in gen_uniq:
                mask = generos == g
                ax.scatter(sub.loc[mask, "edad"], sub.loc[mask, "total"],
                           alpha=0.35, s=18, label=g,
                           color=colores_map[g], zorder=3)
            ax.legend(fontsize=8, facecolor=CARD, edgecolor=BORDER, labelcolor=TXT_MAIN)
        else:
            ax.scatter(sub["edad"], sub["total"], alpha=0.3, s=16, color=ACCENT2, zorder=3)
        # Línea de tendencia
        z = np.polyfit(sub["edad"], sub["total"], 1)
        p = np.poly1d(z)
        x_line = np.linspace(sub["edad"].min(), sub["edad"].max(), 100)
        ax.plot(x_line, p(x_line), color=ACCENT4, linewidth=1.8, linestyle="--", label="Tendencia")
        r = self.analizador.correlacion_edad_gasto()
        ax.set_title(f"Edad vs. Gasto  (r = {r:.3f})", pad=10)
        ax.set_xlabel("Edad")
        ax.set_ylabel("Monto ($)")
        _fmt_miles(ax)
        ax.grid(color=BORDER, linestyle="--", alpha=0.3, zorder=0)
        plt.tight_layout()
        return fig

    def _g_boxplot_genero(self):
        if not self._tiene("genero"):
            return None
        generos = sorted(self.df["genero"].dropna().unique())
        datos   = [self.df[self.df["genero"] == g]["total"].dropna() for g in generos]
        if not any(len(d) > 0 for d in datos):
            return None
        fig, ax = plt.subplots(figsize=(6, 4))
        _apply_dark_style(ax, fig)
        bp = ax.boxplot(datos, labels=generos, patch_artist=True, notch=False,
                        medianprops=dict(color=ACCENT3, linewidth=2),
                        whiskerprops=dict(color=TXT_SUB),
                        capprops=dict(color=TXT_SUB),
                        flierprops=dict(marker="o", color=ACCENT4, alpha=0.4, markersize=3))
        for patch, color in zip(bp["boxes"], PALETTE):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_title("Distribución del gasto por género", pad=10)
        ax.set_ylabel("Monto ($)")
        _fmt_miles(ax)
        ax.grid(axis="y", color=BORDER, linestyle="--", alpha=0.4, zorder=0)
        plt.tight_layout()
        return fig

    def _g_barras_agrupadas(self):
        if self.df.empty:
            return None
        temps = sorted(self.df["temporada"].dropna().unique())
        cats  = self.analizador.ventas_por_categoria().head(4).index.tolist()
        if not cats or not temps:
            return None
        x    = np.arange(len(cats))
        ancho = 0.8 / len(temps)
        fig, ax = plt.subplots(figsize=(8, 4.2))
        _apply_dark_style(ax, fig)
        for i, temp in enumerate(temps):
            sub = self.df[self.df["temporada"] == temp]
            vals = [sub[sub["categoria"] == c]["total"].sum() for c in cats]
            ax.bar(x + i * ancho - 0.4 + ancho / 2, vals,
                   width=ancho * 0.85, label=temp,
                   color=PALETTE[i], zorder=3)
        ax.set_xticks(x)
        ax.set_xticklabels(cats, fontsize=9, color=TXT_SUB)
        ax.set_title("Ventas por categoría y temporada", pad=10)
        _fmt_miles(ax)
        ax.grid(axis="y", color=BORDER, linestyle="--", alpha=0.4, zorder=0)
        ax.legend(fontsize=8, facecolor=CARD, edgecolor=BORDER, labelcolor=TXT_MAIN)
        plt.tight_layout()
        return fig

    def _g_envio(self):
        if not self._tiene("tipo_envio"):
            return None
        datos = self.analizador.ventas_por_tipo_envio()
        if datos.empty:
            return None
        fig, ax = plt.subplots(figsize=(7, 4))
        _apply_dark_style(ax, fig)
        ax.barh(datos.index, datos.values, color=PALETTE[:len(datos)],
                height=0.6, zorder=3)
        ax.set_title("Ingresos por tipo de envío", pad=10)
        _fmt_miles(ax, axis="x")
        ax.grid(axis="x", color=BORDER, linestyle="--", alpha=0.4, zorder=0)
        plt.tight_layout()
        return fig

    # ════════════════════════════════════════════════════════════
    # PESTAÑA 4 — ANÁLISIS AVANZADO
    # ════════════════════════════════════════════════════════════

    def _construir_tab_avanzado(self):
        frame = tk.Frame(self.nb, bg=BG)
        self.nb.add(frame, text="  🔬 Análisis  ")

        canvas_scroll = tk.Canvas(frame, bg=BG, highlightthickness=0)
        scrollbar     = ttk.Scrollbar(frame, orient="vertical", command=canvas_scroll.yview)
        self._frame_avanzado_inner = tk.Frame(canvas_scroll, bg=BG)

        self._frame_avanzado_inner.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(
                scrollregion=canvas_scroll.bbox("all"))
        )
        canvas_scroll.create_window((0, 0), window=self._frame_avanzado_inner, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas_scroll.pack(side="left", fill="both", expand=True)

        # Bind mousewheel
        canvas_scroll.bind_all("<MouseWheel>", lambda e: canvas_scroll.yview_scroll(
            int(-1 * (e.delta / 120)), "units"))

    def _actualizar_avanzado(self):
        if self.analizador is None or self.df.empty:
            return
        inner = self._frame_avanzado_inner
        for w in inner.winfo_children():
            w.destroy()

        def seccion(titulo, color=ACCENT2):
            tk.Frame(inner, bg=color, height=2).pack(fill="x", padx=16, pady=(16, 4))
            tk.Label(inner, text=titulo, font=F_SUBTITLE,
                     bg=BG, fg=color).pack(anchor="w", padx=20)

        def fila_metrica(label, valor, color=TXT_MAIN):
            f = tk.Frame(inner, bg=BG)
            f.pack(fill="x", padx=24, pady=1)
            tk.Label(f, text=label, font=F_SMALL, bg=BG, fg=TXT_SUB, width=36,
                     anchor="w").pack(side="left")
            tk.Label(f, text=str(valor), font=("Segoe UI", 10, "bold"),
                     bg=BG, fg=color).pack(side="left")

        def serie_tabla(titulo, serie: pd.Series, fmt_val="$"):
            if isinstance(serie, pd.Series) and serie.empty:
                return
            seccion(titulo, ACCENT5)
            for k, v in serie.items():
                val_str = f"${float(v):,.2f}" if fmt_val == "$" else f"{v}"
                fila_metrica(str(k), val_str)

        # ── Estadísticas descriptivas ──
        seccion("📊 Estadísticas descriptivas", ACCENT1)
        stats = self.analizador.estadisticas_precio()
        for k, label in [("media", "Ticket promedio"), ("mediana", "Mediana"),
                         ("std", "Desv. estándar"), ("p25", "Percentil 25"),
                         ("p75", "Percentil 75"), ("rango_iqr", "Rango IQR"),
                         ("min", "Precio mínimo"), ("max", "Precio máximo")]:
            fila_metrica(label, f"${stats[k]:,.2f}", ACCENT1)

        # ── Descuentos y promos ──
        desc_info = self.analizador.uso_descuentos()
        if desc_info:
            seccion("🏷️  Descuentos y Promociones", ACCENT3)
            fila_metrica("% ventas con descuento", f"{desc_info['pct_con_descuento']}%", ACCENT3)
            fila_metrica("Ticket promedio CON descuento", f"${desc_info['ticket_con_descuento']:,.2f}")
            fila_metrica("Ticket promedio SIN descuento", f"${desc_info['ticket_sin_descuento']:,.2f}")
            promo = self.analizador.impacto_codigo_promo()
            if promo:
                fila_metrica("% uso de código promo", f"{promo['pct_uso_promo']}%", ACCENT3)
                fila_metrica("Ticket CON código promo", f"${promo['ticket_con_promo']:,.2f}")
                fila_metrica("Ticket SIN código promo", f"${promo['ticket_sin_promo']:,.2f}")

        # ── Fidelización ──
        fid = self.analizador.clientes_recurrentes_vs_nuevos()
        if fid:
            seccion("🔄 Fidelización de clientes", ACCENT2)
            fila_metrica("% clientes recurrentes", f"{fid['pct_recurrentes']}%", ACCENT2)
            fila_metrica("Ticket promedio recurrente", f"${fid['ticket_recurrente']:,.2f}")
            fila_metrica("Ticket promedio nuevo",      f"${fid['ticket_nuevo']:,.2f}")
            fila_metrica("Número recurrentes",  str(fid["n_recurrentes"]))
            fila_metrica("Número nuevos",        str(fid["n_nuevos"]))

        # ── Perfil demográfico ──
        edad_info = self.analizador.distribucion_edad()
        if edad_info:
            seccion("👥 Perfil demográfico — Edad", ACCENT4)
            for k, label in [("media", "Edad promedio"), ("mediana", "Mediana"),
                             ("min", "Edad mínima"), ("max", "Edad máxima"),
                             ("std", "Desv. estándar")]:
                v = edad_info[k]
                fila_metrica(label, f"{v:.1f} años" if isinstance(v, float) else f"{v} años", ACCENT4)

        ventas_edad = self.analizador.ventas_por_grupo_edad()
        if not ventas_edad.empty:
            serie_tabla("Ventas por rango etario", ventas_edad)

        # ── Correlaciones ──
        seccion("🔗 Correlaciones", ACCENT5)
        correlaciones = [
            ("Edad ↔ Gasto",              self.analizador.correlacion_edad_gasto()),
            ("Compras previas ↔ Gasto",   self.analizador.correlacion_compras_previas_gasto()),
            ("Calificación ↔ Gasto",      self.analizador.correlacion_calificacion_gasto()),
        ]
        for label, r in correlaciones:
            if not (isinstance(r, float) and r != r):  # nan check
                fuerza = "débil" if abs(r) < 0.3 else ("moderada" if abs(r) < 0.6 else "fuerte")
                dir_   = "positiva" if r > 0 else "negativa"
                fila_metrica(label, f"r = {r:.3f}  ({fuerza} {dir_})", ACCENT5)

        # ── Calificaciones ──
        dist_calif = self.analizador.distribucion_calificaciones()
        if not dist_calif.empty:
            seccion("⭐ Distribución de calificaciones", ACCENT3)
            for estrellas, conteo in dist_calif.items():
                fila_metrica(f"{'★' * int(estrellas)} ({estrellas} ★)",
                             f"{conteo:,} reseñas", ACCENT3)

        # ── Género ──
        ventas_gen = self.analizador.ventas_por_genero()
        if not ventas_gen.empty:
            serie_tabla("Ventas por género", ventas_gen)

        # ── Ubicaciones ──
        top_ub = self.analizador.top_ubicaciones(15)
        if not top_ub.empty:
            serie_tabla("Top 15 ubicaciones por ingresos", top_ub)

    # ════════════════════════════════════════════════════════════
    # PESTAÑA 5 — EXPORTAR
    # ════════════════════════════════════════════════════════════

    def _construir_tab_exportar(self):
        frame = tk.Frame(self.nb, bg=BG)
        self.nb.add(frame, text="  💾 Exportar  ")

        # Centro
        center = tk.Frame(frame, bg=BG)
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="Exportar reportes",
                 font=F_TITLE, bg=BG, fg=TXT_MAIN).pack(pady=(0, 6))
        tk.Label(center,
                 text="Elige el formato y la carpeta de destino.",
                 font=F_BODY, bg=BG, fg=TXT_SUB).pack(pady=(0, 28))

        # Carpeta
        fila_dir = tk.Frame(center, bg=BG)
        fila_dir.pack(fill="x", pady=6)
        tk.Label(fila_dir, text="Carpeta:", font=F_BODY, bg=BG, fg=TXT_SUB, width=12,
                 anchor="w").pack(side="left")
        self._var_carpeta = tk.StringVar(value=os.path.expanduser("~"))
        ttk.Entry(fila_dir, textvariable=self._var_carpeta, width=36).pack(side="left", padx=6)
        tk.Button(fila_dir, text="📁", command=self._elegir_carpeta,
                  bg=PANEL, fg=TXT_MAIN, font=F_BODY,
                  relief="flat", cursor="hand2", padx=4).pack(side="left")

        # Botones de exportación
        botones_exp = [
            ("  📄 Exportar CSV completo  ",   ACCENT1, self._exp_csv),
            ("  📝 Exportar resumen TXT   ",   ACCENT3, self._exp_txt),
            ("  🖼️  Exportar gráfica actual  ", ACCENT2, self._exp_png_actual),
            ("  🖼️  Exportar todas las gráficas", ACCENT5, self._exp_png_todas),
        ]
        for texto, color, cmd in botones_exp:
            tk.Button(center, text=texto, command=cmd,
                      font=F_BODY, bg=color, fg=BG,
                      activebackground=BG, activeforeground=color,
                      relief="flat", cursor="hand2",
                      padx=12, pady=8, width=34).pack(pady=6)

        self._lbl_exp_status = tk.Label(center, text="",
                                         font=F_SMALL, bg=BG, fg=ACCENT1, wraplength=400)
        self._lbl_exp_status.pack(pady=10)

    def _elegir_carpeta(self):
        carpeta = filedialog.askdirectory(initialdir=self._var_carpeta.get())
        if carpeta:
            self._var_carpeta.set(carpeta)

    def _exp_csv(self):
        if self.df.empty:
            messagebox.showwarning("Sin datos", "No hay datos cargados.")
            return
        try:
            ruta = exportar_csv(self.df, self._var_carpeta.get())
            self._lbl_exp_status.config(text=f"✅ CSV guardado:\n{ruta}", fg=ACCENT1)
        except Exception as e:
            self._lbl_exp_status.config(text=f"❌ Error: {e}", fg=ACCENT4)

    def _exp_txt(self):
        if self.analizador is None:
            messagebox.showwarning("Sin datos", "No hay datos cargados.")
            return
        try:
            resumen = self.analizador.resumen_general(imprimir=False)
            ruta    = exportar_txt(resumen, self._var_carpeta.get())
            self._lbl_exp_status.config(text=f"✅ TXT guardado:\n{ruta}", fg=ACCENT1)
        except Exception as e:
            self._lbl_exp_status.config(text=f"❌ Error: {e}", fg=ACCENT4)

    def _exp_png_actual(self):
        if not hasattr(self, "_fig_actual") or self._fig_actual is None:
            messagebox.showinfo("Sin gráfica",
                                "Ve a la pestaña Gráficas y selecciona una primero.")
            return
        try:
            nombre = self._var_grafica.get().replace(" ", "_").replace("—", "").strip()
            ruta   = exportar_grafica_png(self._fig_actual, nombre, self._var_carpeta.get())
            self._lbl_exp_status.config(text=f"✅ PNG guardado:\n{ruta}", fg=ACCENT1)
        except Exception as e:
            self._lbl_exp_status.config(text=f"❌ Error: {e}", fg=ACCENT4)

    def _exp_png_todas(self):
        if not self._figuras_galeria:
            messagebox.showinfo("Sin gráficas",
                                "Abre cada gráfica en la pestaña Gráficas primero.")
            return
        try:
            rutas = []
            for nombre, fig in self._figuras_galeria.items():
                n = nombre.replace(" ", "_").replace("—", "").strip()
                rutas.append(exportar_grafica_png(fig, n, self._var_carpeta.get()))
            self._lbl_exp_status.config(
                text=f"✅ {len(rutas)} PNGs guardados en:\n{self._var_carpeta.get()}",
                fg=ACCENT1)
        except Exception as e:
            self._lbl_exp_status.config(text=f"❌ Error: {e}", fg=ACCENT4)

    # ════════════════════════════════════════════════════════════
    # CARGA DE DATOS
    # ════════════════════════════════════════════════════════════

    def _cargar_csv_inicio(self):
        try:
            self.sistema.cargar_csv(RUTA_CSV)
            self.df         = self.sistema.obtener_dataframe()
            self.analizador = Analizador(self.df)
            n_p = len(self.sistema.obtener_productos())
            n_v = len(self.sistema.obtener_ventas())
            self._lbl_estado.config(
                text=f"✓  {n_p} productos  ·  {n_v:,} transacciones", fg=ACCENT1)
            self._poblar_combos_tabla()
            self._filtrar_tabla()
            self._actualizar_dashboard()
            self._actualizar_avanzado()
            # Pre-cargar primera gráfica de galería
            self._mostrar_grafica_seleccionada()
        except FileNotFoundError:
            self._lbl_estado.config(text="⚠ CSV no encontrado", fg=ACCENT4)
            messagebox.showerror("Archivo no encontrado",
                                  f"Coloca el CSV en:\n{RUTA_CSV}")
        except Exception as e:
            self._lbl_estado.config(text="⚠ Error al cargar", fg=ACCENT4)
            messagebox.showerror("Error al cargar datos", str(e))

    # ════════════════════════════════════════════════════════════
    # HELPERS DE UI
    # ════════════════════════════════════════════════════════════

    def _tiene(self, col: str) -> bool:
        return col in self.df.columns and not self.df[col].isna().all()

    def _limpiar_frame(self, frame: tk.Frame):
        for widget in frame.winfo_children():
            widget.destroy()
        plt.close("all")

    def _incrustar_figura(self, fig, parent: tk.Frame,
                           side="top", fill=True, expand=True):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        widget = canvas.get_tk_widget()
        if fill and expand:
            widget.pack(fill="both", expand=True)
        else:
            widget.pack(side=side, fill="both", expand=True)
        return canvas

    def _exportar_grafica_actual(self):
        if not hasattr(self, "_fig_actual") or self._fig_actual is None:
            messagebox.showinfo("Sin gráfica", "Selecciona una gráfica primero.")
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Todos", "*.*")],
            initialfile="grafica_ventas.png",
        )
        if not ruta:
            return
        try:
            self._fig_actual.savefig(ruta, dpi=150, bbox_inches="tight",
                                      facecolor=self._fig_actual.get_facecolor())
            messagebox.showinfo("Exportado", f"Gráfica guardada en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))


# ═══════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app  = AplicacionVentas(root)
    root.mainloop()