import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from .constants import *

class TabDashboard:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg=BG)
        notebook.add(self.frame, text="  📊 Dashboard  ")

        # Fila de KPIs
        self._frame_kpis = tk.Frame(self.frame, bg=BG)
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

        # Dos gráficas lado a lado: categorías + temporadas + top 5
        self._frame_dash_charts = tk.Frame(self.frame, bg=BG)
        self._frame_dash_charts.pack(fill="both", expand=True, padx=12, pady=4)

    def actualizar(self):
        if self.app.analizador is None or self.app.df.empty:
            return

        stats = self.app.analizador.estadisticas_precio()

        self._kpi_vars["total_ventas"].set(f"${stats.get('total', 0.0):,.0f}")
        self._kpi_vars["n_ventas"].set(f"{stats.get('n', 0):,}")
        self._kpi_vars["ticket_prom"].set(f"${stats.get('media', 0.0):,.2f}")
        self._kpi_vars["n_productos"].set(str(len(self.app.sistema.obtener_productos())))
        prom_calif = float(self.app.df["calificacion"][self.app.df["calificacion"] > 0].mean()) if self.app._tiene("calificacion") else 0
        self._kpi_vars["calif_prom"].set(f"{'★'*round(prom_calif)} {prom_calif:.1f}" if prom_calif else "—")

        # Limpiar gráficas anteriores
        self.app._limpiar_frame(self._frame_dash_charts)
        plt.close("all")

        # Gráfica izquierda: barras por categoría
        fig1, ax1 = plt.subplots(figsize=(4.8, 3.2))
        apply_dark_style(ax1, fig1)
        datos_cat = self.app.analizador.ventas_por_categoria()
        ax1.bar(datos_cat.index, datos_cat.values,
                color=PALETTE[:len(datos_cat)], width=0.6, zorder=3)
        ax1.set_title("Ingresos por categoría", fontsize=10, pad=8)
        ax1.set_xlabel("")
        fmt_miles(ax1)
        ax1.grid(axis="y", color=BORDER, linestyle="--", alpha=0.5, zorder=0)
        ax1.tick_params(axis="x", rotation=15)
        plt.tight_layout()
        self.app._incrustar_figura(fig1, self._frame_dash_charts, side="left")

        # Gráfica centro: pie de temporadas
        fig2, ax2 = plt.subplots(figsize=(4.0, 3.2))
        fig2.patch.set_facecolor(PANEL)
        datos_temp = self.app.analizador.ventas_por_temporada()
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
        self.app._incrustar_figura(fig2, self._frame_dash_charts, side="left")

        # Gráfica derecha: top 5 productos
        fig3, ax3 = plt.subplots(figsize=(4.8, 3.2))
        apply_dark_style(ax3, fig3)
        top5 = self.app.analizador.top_productos_ingreso(5).sort_values()
        ax3.barh(top5.index, top5.values, color=ACCENT2, height=0.6, zorder=3)
        ax3.set_title("Top 5 productos", fontsize=10, pad=8)
        fmt_miles(ax3, axis="x")
        ax3.grid(axis="x", color=BORDER, linestyle="--", alpha=0.5, zorder=0)
        plt.tight_layout()
        self.app._incrustar_figura(fig3, self._frame_dash_charts, side="left")
