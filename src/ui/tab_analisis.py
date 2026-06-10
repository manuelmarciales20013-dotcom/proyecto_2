import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from .constants import *

class TabAnalisis:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg=BG)
        notebook.add(self.frame, text="  🔬 Análisis  ")

        canvas_scroll = tk.Canvas(self.frame, bg=BG, highlightthickness=0)
        scrollbar     = ttk.Scrollbar(self.frame, orient="vertical", command=canvas_scroll.yview)
        self._frame_avanzado_inner = tk.Frame(canvas_scroll, bg=BG)

        self._frame_avanzado_inner.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )
        canvas_scroll.create_window((0, 0), window=self._frame_avanzado_inner, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas_scroll.pack(side="left", fill="both", expand=True)
        canvas_scroll.bind_all("<MouseWheel>", lambda e: canvas_scroll.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def actualizar(self):
        if self.app.analizador is None or self.app.df.empty: return
        inner = self._frame_avanzado_inner
        for w in inner.winfo_children(): w.destroy()

        def seccion(titulo, color=ACCENT2):
            tk.Frame(inner, bg=color, height=2).pack(fill="x", padx=16, pady=(16, 4))
            tk.Label(inner, text=titulo, font=F_SUBTITLE, bg=BG, fg=color).pack(anchor="w", padx=20)

        def fila_metrica(label, valor, color=TXT_MAIN):
            f = tk.Frame(inner, bg=BG)
            f.pack(fill="x", padx=24, pady=1)
            tk.Label(f, text=label, font=F_SMALL, bg=BG, fg=TXT_SUB, width=36, anchor="w").pack(side="left")
            tk.Label(f, text=str(valor), font=("Segoe UI", 10, "bold"), bg=BG, fg=color).pack(side="left")

        def serie_tabla(titulo, serie: pd.Series, fmt_val="$"):
            if isinstance(serie, pd.Series) and serie.empty: return
            seccion(titulo, ACCENT5)
            for k, v in serie.items():
                val_str = f"${float(v):,.2f}" if fmt_val == "$" else f"{v}"
                fila_metrica(str(k), val_str)

        seccion("📊 Estadísticas descriptivas", ACCENT1)
        stats = self.app.analizador.estadisticas_precio()
        for k, label in [("media", "Ticket promedio"), ("mediana", "Mediana"),
                         ("std", "Desv. estándar"), ("p25", "Percentil 25"),
                         ("p75", "Percentil 75"), ("rango_iqr", "Rango IQR"),
                         ("min", "Precio mínimo"), ("max", "Precio máximo")]:
            if k in stats: fila_metrica(label, f"${stats[k]:,.2f}", ACCENT1)

        desc_info = self.app.analizador.uso_descuentos()
        if desc_info:
            seccion("🏷️  Descuentos y Promociones", ACCENT3)
            fila_metrica("% ventas con descuento", f"{desc_info['pct_con_descuento']}%", ACCENT3)
            fila_metrica("Ticket promedio CON descuento", f"${desc_info['ticket_con_descuento']:,.2f}")
            fila_metrica("Ticket promedio SIN descuento", f"${desc_info['ticket_sin_descuento']:,.2f}")
            promo = self.app.analizador.impacto_codigo_promo()
            if promo:
                fila_metrica("% uso de código promo", f"{promo['pct_uso_promo']}%", ACCENT3)
                fila_metrica("Ticket CON código promo", f"${promo['ticket_con_promo']:,.2f}")
                fila_metrica("Ticket SIN código promo", f"${promo['ticket_sin_promo']:,.2f}")

        fid = self.app.analizador.clientes_recurrentes_vs_nuevos()
        if fid:
            seccion("🔄 Fidelización de clientes", ACCENT2)
            fila_metrica("% clientes recurrentes", f"{fid['pct_recurrentes']}%", ACCENT2)
            fila_metrica("Ticket promedio recurrente", f"${fid['ticket_recurrente']:,.2f}")
            fila_metrica("Ticket promedio nuevo",      f"${fid['ticket_nuevo']:,.2f}")
            fila_metrica("Número recurrentes",  str(fid["n_recurrentes"]))
            fila_metrica("Número nuevos",        str(fid["n_nuevos"]))

        edad_info = self.app.analizador.distribucion_edad()
        if edad_info:
            seccion("👥 Perfil demográfico — Edad", ACCENT4)
            for k, label in [("media", "Edad promedio"), ("mediana", "Mediana"),
                             ("min", "Edad mínima"), ("max", "Edad máxima"),
                             ("std", "Desv. estándar")]:
                v = edad_info.get(k)
                if v is not None: fila_metrica(label, f"{v:.1f} años" if isinstance(v, float) else f"{v} años", ACCENT4)

        ventas_edad = self.app.analizador.ventas_por_grupo_edad()
        if not ventas_edad.empty: serie_tabla("Ventas por rango etario", ventas_edad)

        seccion("🔗 Correlaciones", ACCENT5)
        correlaciones = [
            ("Edad ↔ Gasto",              self.app.analizador.correlacion_edad_gasto()),
            ("Compras previas ↔ Gasto",   self.app.analizador.correlacion_compras_previas_gasto()),
            ("Calificación ↔ Gasto",      self.app.analizador.correlacion_calificacion_gasto()),
        ]
        for label, r in correlaciones:
            if not (isinstance(r, float) and r != r):
                fuerza = "débil" if abs(r) < 0.3 else ("moderada" if abs(r) < 0.6 else "fuerte")
                dir_   = "positiva" if r > 0 else "negativa"
                fila_metrica(label, f"r = {r:.3f}  ({fuerza} {dir_})", ACCENT5)

        dist_calif = self.app.analizador.distribucion_calificaciones()
        if not dist_calif.empty:
            seccion("⭐ Distribución de calificaciones", ACCENT3)
            for estrellas, conteo in dist_calif.items():
                fila_metrica(f"{'★' * int(estrellas)} ({estrellas} ★)", f"{conteo:,} reseñas", ACCENT3)

        ventas_gen = self.app.analizador.ventas_por_genero()
        if not ventas_gen.empty: serie_tabla("Ventas por género", ventas_gen)

        top_ub = self.app.analizador.top_ubicaciones(15)
        if not top_ub.empty: serie_tabla("Top 15 ubicaciones por ingresos", top_ub)
