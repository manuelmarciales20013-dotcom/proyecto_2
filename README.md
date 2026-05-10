# Sistema de Análisis de Ventas

Proyecto educativo en Python para registrar ventas y calcular métricas comerciales.

## Descripción

El sistema permite:
- Registrar productos y ventas (manual o mediante datos simulados).
- Calcular métricas: total de ventas, producto más/menos vendido, ingreso promedio por venta y por producto.

Visualizaciones y dashboard: pendiente — se implementarán en una fase posterior.

El proyecto está pensado para usarse con Python y librerías de análisis (`pandas`, `numpy`).

## Estructura de archivos

- `main.py` — Menú interactivo y helpers para demo.
- `producto.py` — Clase `Producto` (validaciones, getters, __str__).
- `venta.py` — Clase `Venta` (composición con `Producto`, total por venta).
- `generador.py` — Funciones para crear catálogo y ventas simuladas (útil para pruebas).
- `sistema_ventas.py` — Clase `SistemaDeVentas` (registro, listados, DataFrame).
- `analizador.py` — Clase `Analizador` (métricas sobre DataFrame con `pandas`).
- `exceptions.py` — Excepciones específicas del sistema.
- `requirements.txt` — Dependencias del proyecto.
- `README.md` — Este archivo.

## Requisitos

- Python 3.10+ recomendado (probado en 3.14).
- `requirements.txt` incluye: `pandas`, `numpy`.

## Instalación (Windows / PowerShell)

1. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Nota: No incluyas un entorno virtual dentro del directorio del proyecto si vas a subirlo a GitHub. Si deseas usar un entorno virtual, créalo fuera de la carpeta del proyecto o ignóralo con `.gitignore` (recomendado).

Si ya agregaste la carpeta del entorno virtual al repositorio, quita sus archivos del control de versiones antes de hacer push:

```powershell
git rm -r --cached .venv
git commit -m "Remove venv from repo"
git push
```

## Uso — Menú interactivo

Ejecuta la aplicación:

```powershell
python main.py
```

Opciones principales del menú:
1) Generar datos simulados — crea catálogo y ventas de prueba (útil para desarrollo).  
2) Registrar producto — entrada manual de `Producto`.  
3) Registrar venta — elige producto y cantidad para crear una `Venta`.  
4) Listar productos — muestra el catálogo.  
5) Listar ventas — muestra las ventas registradas.  
6) Ver métricas — usa `Analizador` para imprimir resumen.  
7) Salir.

> Nota: El generador de datos se incluye para pruebas; antes de una demostración final puedes optar por no usarlo y registrar productos manualmente.

## Uso rápido (ejemplo en REPL)

Ejemplo para generar datos y ver el resumen con `Analizador`:

```python
from main import crear_sistema_con_datos
from analizador import Analizador

s = crear_sistema_con_datos(n=30, seed=2026)
df = s.obtener_dataframe()
Analizador(df).resumen_general()
```

## Pruebas y próximos pasos

- `Escribir pruebas y ejemplos` está pendiente: se recomienda añadir tests con `pytest` o pequeños scripts `demo_*.py` que automaticen casos.
- Puedes personalizar `generador.py` para cambiar catálogo, distribución y semillas.
- Visualizaciones (dashboard) serán implementadas en una próxima iteración.

## Solución de problemas

- Si falta alguna librería: `pip install -r requirements.txt`.
- Si hay problemas con acentos en salida, revisa la codificación de la terminal.

---


