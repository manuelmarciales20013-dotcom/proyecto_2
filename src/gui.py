"""gui.py  ──  Sistema de Análisis de Ventas  ──  v2.0
Interfaz rediseñada y modularizada (MVC).
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")

from sistema_ventas import SistemaDeVentas
from analizador import Analizador

# Importar constantes y tabs del paquete ui
from ui.constants import *
from ui.tab_dashboard import TabDashboard
from ui.tab_tabla import TabTabla
from ui.tab_graficas import TabGraficas
from ui.tab_analisis import TabAnalisis
from ui.tab_exportar import TabExportar
from ui.tab_registro import TabRegistro

class AplicacionVentas:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistema de Análisis de Ventas  v2.0")
        self.root.geometry("1180x720")
        self.root.configure(bg=BG)
        self.root.minsize(900, 600)

        self.sistema = SistemaDeVentas()
        self.df = pd.DataFrame()
        self.analizador = None
        self._figuras_galeria: dict = {}
        self.ruta_csv_actual = RUTA_CSV

        self._configurar_estilos()
        self._construir_interfaz()
        self._cargar_csv_inicio()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=[4, 4, 0, 0])
        style.configure("TNotebook.Tab", background=PANEL, foreground=TXT_SUB,
                         font=F_BODY, padding=[14, 7], borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", CARD), ("active", BORDER)],
                  foreground=[("selected", ACCENT1), ("active", TXT_MAIN)])

        style.configure("Treeview", background=CARD, foreground=TXT_MAIN,
                         fieldbackground=CARD, rowheight=24, borderwidth=0, font=F_SMALL)
        style.configure("Treeview.Heading", background=PANEL, foreground=ACCENT2,
                         font=("Segoe UI", 9, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", ACCENT2)], foreground=[("selected", BG)])

        style.configure("TScrollbar", background=BORDER, troughcolor=PANEL, borderwidth=0, arrowcolor=TXT_SUB)
        style.configure("TCombobox", background=CARD, foreground=TXT_MAIN,
                         fieldbackground=CARD, selectbackground=ACCENT2, font=F_SMALL)
        style.configure("TEntry", background=CARD, foreground=TXT_MAIN,
                         insertcolor=TXT_MAIN, fieldbackground=CARD, font=F_SMALL)

    def _construir_interfaz(self):
        # Header
        hdr = tk.Frame(self.root, bg=PANEL, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="◈  SALES INTELLIGENCE DASHBOARD", font=("Segoe UI", 13, "bold"),
                 bg=PANEL, fg=ACCENT1).pack(side="left", padx=20)
        
        self.btn_cargar = tk.Button(
            hdr, text="Cargar otro CSV", command=self._cargar_csv_manual,
            font=F_SMALL, bg=ACCENT1, fg=BG, activebackground=BG, activeforeground=ACCENT1,
            relief="flat", cursor="hand2", padx=10, pady=3
        )
        self.btn_cargar.pack(side="right", padx=(10, 20))

        self._lbl_estado = tk.Label(hdr, text="Cargando…", font=F_SMALL, bg=PANEL, fg=TXT_SUB)
        self._lbl_estado.pack(side="right", padx=10)

        # Notebook
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        # Instanciar Tabs
        self.tab_dashboard = TabDashboard(self.nb, self)
        self.tab_tabla     = TabTabla(self.nb, self)
        self.tab_graficas  = TabGraficas(self.nb, self)
        self.tab_analisis  = TabAnalisis(self.nb, self)
        self.tab_exportar  = TabExportar(self.nb, self)
        self.tab_registro  = TabRegistro(self.nb, self)

    def _cargar_csv_inicio(self):
        self.root.after(100, lambda: self._procesar_carga_csv(self.ruta_csv_actual))

    def _cargar_csv_manual(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
        )
        if ruta:
            self.ruta_csv_actual = ruta
            self._lbl_estado.config(text="Cargando archivo…", fg=TXT_SUB)
            self.root.update()
            self._procesar_carga_csv(ruta)

    def _procesar_carga_csv(self, ruta: str):
        try:
            self.sistema.limpiar()
            self.sistema.cargar_csv(ruta)
            self._lbl_estado.config(text=f"CSV Cargado: {os.path.basename(ruta)}", fg=ACCENT1)
            self._sincronizar_datos()
        except Exception as e:
            self._lbl_estado.config(text="Error al cargar CSV", fg=ACCENT4)
            messagebox.showerror("Error de Carga", f"No se pudo cargar el archivo:\n{e}")

    def _sincronizar_datos(self):
        self.df = self.sistema.obtener_dataframe()
        if not self.df.empty:
            self.analizador = Analizador(self.df)
            # Actualizar todos los tabs
            self.tab_dashboard.actualizar()
            self.tab_tabla.poblar_combos()
            self.tab_tabla.filtrar_tabla()
            self.tab_analisis.actualizar()
            self.tab_registro.actualizar_combo_productos()
            self.tab_graficas.mostrar_grafica_seleccionada()

    # Helpers
    def _tiene(self, col: str) -> bool:
        return self.analizador._tiene(col) if self.analizador else False

    def _limpiar_frame(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def _incrustar_figura(self, fig, parent, fill=False, expand=False, side="top"):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        w = canvas.get_tk_widget()
        w.pack(side=side, fill="both" if fill else "none", expand=expand)


if __name__ == "__main__":
    root = tk.Tk()
    app  = AplicacionVentas(root)
    root.mainloop()