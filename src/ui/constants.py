import os
import matplotlib
import matplotlib.pyplot as plt

# Paleta y Tipografía
BG          = "#F5F9FD"
PANEL       = "#DDEAF6"
CARD        = "#EBF3FA"
BORDER      = "#BDD7EE"
ACCENT1     = "#1F4E79"
ACCENT2     = "#2E75B6"
ACCENT3     = "#4472C4"
ACCENT4     = "#ED7D31"
ACCENT5     = "#5B9BD5"
TXT_MAIN    = "#172B4D"
TXT_SUB     = "#2E5A8A"
TXT_MUTED   = "#7BA7C9"

PALETTE     = ["#2E75B6", "#1F4E79", "#4472C4", "#9DC3E6", "#5B9BD5",
               "#BDD7EE", "#172B4D", "#70B0D9", "#A8C8E5", "#DDEBF7"]

F_TITLE     = ("Segoe UI", 15, "bold")
F_SUBTITLE  = ("Segoe UI", 11, "bold")
F_BODY      = ("Segoe UI", 10)
F_SMALL     = ("Segoe UI", 9)
F_KPI       = ("Segoe UI", 22, "bold")
F_KPI_LABEL = ("Segoe UI", 9)

# Ruta base para el CSV por defecto (gui.py estará en src/, ui en src/ui/)
RUTA_CSV = os.path.join(os.path.dirname(__file__), "..", "..", "datos", "Ventas.csv")

def apply_dark_style(ax, fig):
    fig.patch.set_facecolor(PANEL)
    ax.set_facecolor(CARD)
    ax.tick_params(colors=TXT_SUB, labelsize=8)
    ax.xaxis.label.set_color(TXT_SUB)
    ax.yaxis.label.set_color(TXT_SUB)
    ax.title.set_color(TXT_MAIN)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.title.set_fontweight("bold")

def fmt_miles(ax, axis="y"):
    fmt = plt.FuncFormatter(lambda x, _: f"${x:,.0f}")
    if axis == "y":
        ax.yaxis.set_major_formatter(fmt)
    else:
        ax.xaxis.set_major_formatter(fmt)
