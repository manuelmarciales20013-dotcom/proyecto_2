# Sistema de Análisis de Ventas 

Dashboard de análisis de datos de ventas construido con Python, pandas, matplotlib y tkinter.


## Funcionalidades
- Dashboard con KPIs en tiempo real
- Tabla interactiva con filtros por categoría, temporada y género
- 9 gráficas (histograma, scatter, boxplot, barras agrupadas...)
- 20+ métricas: correlaciones, análisis demográfico, fidelización
- Exportación a CSV, TXT y PNG

## Tecnologías
Python 3.10+ · pandas · numpy · matplotlib · tkinter

## Instalación
pip install -r requirements.txt
python src/gui.py

## Estructura del proyecto
ProyectoProgramacionVentas/
│
├── src/                          
│   ├── gui.py
│   ├── sistema_ventas.py
│   ├── analizador.py
│   ├── exportador.py
│   ├── producto.py
│   ├── venta.py
│   └── exceptions.py
│
├── datos/
│   └── Ventas.csv              
│
├── requirements.txt
├── .gitignore
└── README.md
## Autor
Jhan Carlos Solano Calderón, Manuel Alejandro marciales tocarruncho  — Universidad Simón Bolívar