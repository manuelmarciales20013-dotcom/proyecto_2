import tkinter as tk
from tkinter import ttk
import pandas as pd
from .constants import *

class TabTabla:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg=BG)
        notebook.add(self.frame, text="  📋 Tabla  ")

        # Barra de filtros
        bar = tk.Frame(self.frame, bg=PANEL, pady=6)
        bar.pack(fill="x")

        tk.Label(bar, text="Buscar:", font=F_SMALL, bg=PANEL, fg=TXT_SUB).pack(side="left", padx=(12, 4))
        self._var_buscar = tk.StringVar()
        self._var_buscar.trace_add("write", lambda *_: self.filtrar_tabla())
        ttk.Entry(bar, textvariable=self._var_buscar, width=22).pack(side="left", padx=4)

        tk.Label(bar, text="Categoría:", font=F_SMALL, bg=PANEL, fg=TXT_SUB).pack(side="left", padx=(12, 4))
        self._var_cat_filtro = tk.StringVar(value="Todas")
        self._combo_cat = ttk.Combobox(bar, textvariable=self._var_cat_filtro, state="readonly", width=16)
        self._combo_cat.pack(side="left", padx=4)
        self._combo_cat.bind("<<ComboboxSelected>>", lambda _: self.filtrar_tabla())

        tk.Label(bar, text="Temporada:", font=F_SMALL, bg=PANEL, fg=TXT_SUB).pack(side="left", padx=(12, 4))
        self._var_temp_filtro = tk.StringVar(value="Todas")
        self._combo_temp = ttk.Combobox(bar, textvariable=self._var_temp_filtro, state="readonly", width=14)
        self._combo_temp.pack(side="left", padx=4)
        self._combo_temp.bind("<<ComboboxSelected>>", lambda _: self.filtrar_tabla())

        tk.Label(bar, text="Género:", font=F_SMALL, bg=PANEL, fg=TXT_SUB).pack(side="left", padx=(12, 4))
        self._var_gen_filtro = tk.StringVar(value="Todos")
        self._combo_gen = ttk.Combobox(bar, textvariable=self._var_gen_filtro, state="readonly", width=10)
        self._combo_gen.pack(side="left", padx=4)
        self._combo_gen.bind("<<ComboboxSelected>>", lambda _: self.filtrar_tabla())

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

        tree_frame = tk.Frame(self.frame, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=6)

        scrolly = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollx = ttk.Scrollbar(tree_frame, orient="horizontal")

        self._tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                  yscrollcommand=scrolly.set, xscrollcommand=scrollx.set,
                                  selectmode="browse")
        scrolly.config(command=self._tree.yview)
        scrollx.config(command=self._tree.xview)

        for col, hdr, w in zip(cols, headers, widths):
            self._tree.heading(col, text=hdr, command=lambda c=col: self._ordenar_tabla(c))
            self._tree.column(col, width=w, minwidth=40, anchor="w")

        self._tree.tag_configure("par",   background=CARD)
        self._tree.tag_configure("impar", background="#F0F7FD")

        scrolly.pack(side="right", fill="y")
        scrollx.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)

        self._df_filtrado = pd.DataFrame()
        self._orden_asc   = {}

    def poblar_combos(self):
        if self.app.df.empty:
            return
        cats  = ["Todas"] + sorted(self.app.df["categoria"].dropna().unique().tolist())
        temps = ["Todas"] + sorted(self.app.df["temporada"].dropna().unique().tolist())
        gens  = ["Todos"] + sorted(self.app.df["genero"].dropna().unique().tolist()) if self.app._tiene("genero") else ["Todos"]
        self._combo_cat["values"]  = cats
        self._combo_temp["values"] = temps
        self._combo_gen["values"]  = gens

    def filtrar_tabla(self):
        if self.app.df.empty:
            return
        d = self.app.df.copy()
        buscar = self._var_buscar.get().strip().lower()
        if buscar:
            d = d[d["producto"].str.lower().str.contains(buscar, na=False)]
        if self._var_cat_filtro.get() != "Todas":
            d = d[d["categoria"] == self._var_cat_filtro.get()]
        if self._var_temp_filtro.get() != "Todas":
            d = d[d["temporada"] == self._var_temp_filtro.get()]
        if self.app._tiene("genero") and self._var_gen_filtro.get() != "Todos":
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
        d = self._df_filtrado if not self._df_filtrado.empty else self.app.df
        try:
            d = d.sort_values(col, ascending=asc)
        except Exception:
            pass
        self._refrescar_tree(d)
