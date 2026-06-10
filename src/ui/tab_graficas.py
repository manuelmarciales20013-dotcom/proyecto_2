import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .constants import *
from exportador import exportar_grafica_png

class TabGraficas:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg=BG)
        notebook.add(self.frame, text="  📈 Gráficas  ")

        # Selector de gráfica
        sel_bar = tk.Frame(self.frame, bg=PANEL, pady=6)
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
        combo.bind("<<ComboboxSelected>>", lambda _: self.mostrar_grafica_seleccionada())

        tk.Button(sel_bar, text="  💾 Exportar PNG  ",
                  command=self.exportar_grafica_actual,
                  font=F_SMALL, bg=ACCENT2, fg=BG,
                  activebackground="#3A7AE0", relief="flat",
                  cursor="hand2", padx=8, pady=3).pack(side="right", padx=12)

        # Canvas de la gráfica
        self._frame_galeria_canvas = tk.Frame(self.frame, bg=BG)
        self._frame_galeria_canvas.pack(fill="both", expand=True)
        self._fig_actual = None

    def mostrar_grafica_seleccionada(self):
        if self.app.analizador is None: return
        nombre = self._var_grafica.get()
        for n, fn in self._graficas_disponibles:
            if n == nombre:
                fig = fn()
                if fig:
                    self._fig_actual = fig
                    self.app._figuras_galeria[nombre] = fig
                    self.app._limpiar_frame(self._frame_galeria_canvas)
                    self.app._incrustar_figura(fig, self._frame_galeria_canvas,
                                           fill=True, expand=True)
                return

    def exportar_grafica_actual(self):
        if not self._fig_actual:
            messagebox.showwarning("Sin gráfica", "No hay ninguna gráfica visible para exportar.")
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            title="Guardar gráfica como..."
        )
        if ruta:
            try:
                res = exportar_grafica_png(self._fig_actual, ruta)
                messagebox.showinfo("Exportación Exitosa", f"Gráfica guardada en:\n{res}")
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al exportar:\n{e}")

    # ── Las 9 gráficas ──────────────────────────────────────────

    def _g_barras_categorias(self):
        datos = self.app.analizador.ventas_por_categoria()
        if datos.empty: return None
        fig, ax = plt.subplots(figsize=(7, 4))
        apply_dark_style(ax, fig)
        ax.bar(datos.index, datos.values, color=PALETTE[:len(datos)], width=0.6, zorder=3)
        ax.set_title("Ingresos totales por categoría", pad=10)
        ax.set_xlabel("Categoría")
        ax.set_ylabel("Total ($)")
        fmt_miles(ax)
        ax.grid(axis="y", color=BORDER, linestyle="--", alpha=0.5, zorder=0)
        ax.tick_params(axis="x", rotation=15)
        plt.tight_layout()
        return fig

    def _g_pie_temporadas(self):
        datos = self.app.analizador.ventas_por_temporada()
        if datos.empty: return None
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
        datos = self.app.analizador.top_productos_ingreso(10).sort_values()
        if datos.empty: return None
        fig, ax = plt.subplots(figsize=(7, 5))
        apply_dark_style(ax, fig)
        bars = ax.barh(datos.index, datos.values, color=ACCENT2, height=0.65, zorder=3)
        ax.set_title("Top 10 productos por ingresos", pad=10)
        ax.set_xlabel("Total ($)")
        fmt_miles(ax, axis="x")
        ax.grid(axis="x", color=BORDER, linestyle="--", alpha=0.5, zorder=0)
        for bar, val in zip(bars, datos.values):
            ax.text(val + datos.values.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                    f"${val:,.0f}", va="center", fontsize=7, color=TXT_SUB)
        plt.tight_layout()
        return fig

    def _g_metodos_pago(self):
        if not self.app._tiene("metodo_pago"): return None
        datos = self.app.analizador.ventas_por_metodo_pago()
        if datos.empty: return None
        fig, ax = plt.subplots(figsize=(7, 4))
        apply_dark_style(ax, fig)
        ax.bar(datos.index, datos.values, color=PALETTE[:len(datos)], width=0.6, zorder=3)
        ax.set_title("Ingresos por método de pago", pad=10)
        fmt_miles(ax)
        ax.grid(axis="y", color=BORDER, linestyle="--", alpha=0.5, zorder=0)
        ax.tick_params(axis="x", rotation=20)
        plt.tight_layout()
        return fig

    def _g_histograma_precios(self):
        fig, ax = plt.subplots(figsize=(7, 4))
        apply_dark_style(ax, fig)
        vals = self.app.df["total"].dropna()
        n, bins, patches = ax.hist(vals, bins=30, color=ACCENT1,
                                    edgecolor=PANEL, linewidth=0.4, zorder=3)
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
        if not self.app._tiene("edad"): return None
        sub = self.app.df[["edad", "total"]].dropna()
        if len(sub) < 10: return None
        fig, ax = plt.subplots(figsize=(7, 4))
        apply_dark_style(ax, fig)
        if self.app._tiene("genero"):
            generos = self.app.df.loc[sub.index, "genero"]
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
        z = np.polyfit(sub["edad"], sub["total"], 1)
        p = np.poly1d(z)
        x_line = np.linspace(sub["edad"].min(), sub["edad"].max(), 100)
        ax.plot(x_line, p(x_line), color=ACCENT4, linewidth=1.8, linestyle="--", label="Tendencia")
        r = self.app.analizador.correlacion_edad_gasto()
        ax.set_title(f"Edad vs. Gasto  (r = {r:.3f})", pad=10)
        ax.set_xlabel("Edad")
        ax.set_ylabel("Monto ($)")
        fmt_miles(ax)
        ax.grid(color=BORDER, linestyle="--", alpha=0.3, zorder=0)
        plt.tight_layout()
        return fig

    def _g_boxplot_genero(self):
        if not self.app._tiene("genero"): return None
        generos = sorted(self.app.df["genero"].dropna().unique())
        datos   = [self.app.df[self.app.df["genero"] == g]["total"].dropna() for g in generos]
        if not any(len(d) > 0 for d in datos): return None
        fig, ax = plt.subplots(figsize=(6, 4))
        apply_dark_style(ax, fig)
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
        fmt_miles(ax)
        ax.grid(axis="y", color=BORDER, linestyle="--", alpha=0.4, zorder=0)
        plt.tight_layout()
        return fig

    def _g_barras_agrupadas(self):
        if self.app.df.empty: return None
        temps = sorted(self.app.df["temporada"].dropna().unique())
        cats  = self.app.analizador.ventas_por_categoria().head(4).index.tolist()
        if not cats or not temps: return None
        x    = np.arange(len(cats))
        ancho = 0.8 / len(temps)
        fig, ax = plt.subplots(figsize=(8, 4.2))
        apply_dark_style(ax, fig)
        for i, temp in enumerate(temps):
            sub = self.app.df[self.app.df["temporada"] == temp]
            vals = [sub[sub["categoria"] == c]["total"].sum() for c in cats]
            ax.bar(x + i * ancho - 0.4 + ancho / 2, vals,
                   width=ancho * 0.85, label=temp,
                   color=PALETTE[i], zorder=3)
        ax.set_xticks(x)
        ax.set_xticklabels(cats, fontsize=9, color=TXT_SUB)
        ax.set_title("Ventas por categoría y temporada", pad=10)
        fmt_miles(ax)
        ax.grid(axis="y", color=BORDER, linestyle="--", alpha=0.4, zorder=0)
        ax.legend(fontsize=8, facecolor=CARD, edgecolor=BORDER, labelcolor=TXT_MAIN)
        plt.tight_layout()
        return fig

    def _g_envio(self):
        if not self.app._tiene("tipo_envio"): return None
        datos = self.app.analizador.ventas_por_tipo_envio()
        if datos.empty: return None
        fig, ax = plt.subplots(figsize=(7, 4))
        apply_dark_style(ax, fig)
        ax.barh(datos.index, datos.values, color=PALETTE[:len(datos)],
                height=0.6, zorder=3)
        ax.set_title("Ingresos por tipo de envío", pad=10)
        fmt_miles(ax, axis="x")
        ax.grid(axis="x", color=BORDER, linestyle="--", alpha=0.4, zorder=0)
        plt.tight_layout()
        return fig
