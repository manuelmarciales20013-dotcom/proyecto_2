import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .constants import *
from exportador import exportar_csv, exportar_txt

class TabExportar:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = tk.Frame(notebook, bg=BG)
        notebook.add(self.frame, text="  💾 Exportar  ")

        # Contenedor central
        center = tk.Frame(self.frame, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        center.place(relx=0.5, rely=0.4, anchor="center", width=500, height=350)

        tk.Label(center, text="Exportar Reportes", font=F_TITLE, bg=CARD, fg=ACCENT1).pack(pady=(25, 10))
        tk.Label(center, text="Seleccione el formato para descargar el informe actual.",
                 font=F_BODY, bg=CARD, fg=TXT_SUB).pack(pady=(0, 25))

        self.var_formato = tk.StringVar(value="CSV")
        f_opc = tk.Frame(center, bg=CARD)
        f_opc.pack(pady=10)

        ttk.Radiobutton(f_opc, text="CSV (Datos Crudos filtrados)", variable=self.var_formato, value="CSV").pack(anchor="w", pady=6)
        ttk.Radiobutton(f_opc, text="TXT (Resumen Ejecutivo)", variable=self.var_formato, value="TXT").pack(anchor="w", pady=6)

        btn = tk.Button(
            center, text="Descargar Reporte", command=self.ejecutar_exportacion,
            font=F_SUBTITLE, bg=ACCENT2, fg=BG,
            activebackground=BG, activeforeground=ACCENT2,
            relief="flat", cursor="hand2", padx=20, pady=8
        )
        btn.pack(pady=30)

    def ejecutar_exportacion(self):
        if self.app.df.empty or self.app.analizador is None:
            messagebox.showwarning("Sin datos", "No hay datos cargados para exportar.")
            return
        formato = self.var_formato.get()
        if formato == "CSV":
            ruta = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Guardar CSV como..."
            )
            if ruta:
                try:
                    res = exportar_csv(self.app.df, ruta)
                    messagebox.showinfo("Éxito", f"Archivo CSV guardado en:\n{res}")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        elif formato == "TXT":
            ruta = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                title="Guardar Reporte TXT como..."
            )
            if ruta:
                try:
                    res = exportar_txt(self.app.analizador.resumen_general(imprimir=False), ruta)
                    messagebox.showinfo("Éxito", f"Reporte TXT guardado en:\n{res}")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
