"""analizador.py
Clase Analizador — 20+ métricas calculadas con pandas y numpy.

Columnas del DataFrame (todas las del CSV):
    producto, categoria, color, talla, suscripcion,
    cantidad, precio_unitario, total, temporada,
    edad, genero, ubicacion, metodo_pago, tipo_envio,
    descuento, codigo_promo, calificacion,
    frecuencia_compra, compras_previas
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple


class Analizador:
    COLUMNAS_REQUERIDAS = {
        "producto", "categoria", "cantidad", "precio_unitario",
        "total", "temporada",
    }
    # Las demás son opcionales (pueden faltar si el CSV es viejo)
    COLUMNAS_EXTENDIDAS = {
        "edad", "genero", "ubicacion", "metodo_pago", "tipo_envio",
        "descuento", "codigo_promo", "calificacion",
        "frecuencia_compra", "compras_previas", "color", "talla", "suscripcion",
    }

    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Analizador requiere un pandas.DataFrame.")
        self.df = df.copy()
        faltantes = self.COLUMNAS_REQUERIDAS - set(self.df.columns)
        if faltantes:
            raise ValueError(f"Faltan columnas requeridas: {faltantes}")
        # Detectar qué columnas extendidas están disponibles
        self._ext = self.COLUMNAS_EXTENDIDAS & set(self.df.columns)

    def _tiene(self, col: str) -> bool:
        return col in self._ext and not self.df[col].isna().all()

    # ════════════════════════════════════════════════════════════
    # HELPERS INTERNOS
    # ════════════════════════════════════════════════════════════

    def _agrupar(self, col_group: str, col_val: str, func: str = "sum", sort: bool = True, asc: bool = False, head: int = None, filter_mask: pd.Series = None) -> pd.Series:
        if not self._tiene(col_group) and col_group not in self.COLUMNAS_REQUERIDAS:
            return pd.Series(dtype=float)
        
        d = self.df if filter_mask is None else self.df[filter_mask]
        
        grouped = d.groupby(col_group)[col_val].agg(func)
        if sort:
            grouped = grouped.sort_values(ascending=asc)
        if head:
            grouped = grouped.head(head)
        return grouped

    def _correlacion(self, col_a: str, col_b: str) -> float:
        if not self._tiene(col_a) and col_a not in self.COLUMNAS_REQUERIDAS:
            return float("nan")
        if not self._tiene(col_b) and col_b not in self.COLUMNAS_REQUERIDAS:
            return float("nan")
            
        sub = self.df[[col_a, col_b]].dropna()
        if len(sub) < 2:
            return float("nan")
        return float(np.corrcoef(sub[col_a], sub[col_b])[0, 1])

    # ════════════════════════════════════════════════════════════
    # MÉTRICAS ORIGINALES
    # ════════════════════════════════════════════════════════════

    def total_ventas(self) -> float:
        return float(self.df["total"].sum()) if not self.df.empty else 0.0

    def producto_mas_vendido(self) -> pd.Series:
        return self._agrupar("producto", "cantidad", head=1)

    def producto_menos_demanda(self) -> pd.Series:
        return self._agrupar("producto", "cantidad", asc=True, head=1)

    def ingreso_promedio_por_venta(self) -> float:
        return float(self.df["total"].mean()) if not self.df.empty else 0.0

    def ingreso_promedio_por_producto(self) -> pd.Series:
        return self._agrupar("producto", "total", func="mean")

    def ventas_por_categoria(self) -> pd.Series:
        return self._agrupar("categoria", "total")

    def unidades_por_categoria(self) -> pd.Series:
        return self._agrupar("categoria", "cantidad")

    def ventas_por_temporada(self) -> pd.Series:
        return self._agrupar("temporada", "total")

    # ════════════════════════════════════════════════════════════
    # MÉTRICAS NUEVAS — ESTADÍSTICAS DESCRIPTIVAS
    # ════════════════════════════════════════════════════════════

    def estadisticas_precio(self) -> Dict[str, float]:
        """Media, mediana, desv. estándar, percentil 25/75 y rango del precio."""
        s = self.df["total"]
        if s.empty:
            return {}
        return {
            "media":     float(s.mean()),
            "mediana":   float(s.median()),
            "std":       float(s.std()),
            "min":       float(s.min()),
            "max":       float(s.max()),
            "p25":       float(np.percentile(s, 25)),
            "p75":       float(np.percentile(s, 75)),
            "rango_iqr": float(np.percentile(s, 75) - np.percentile(s, 25)),
            "total":     float(s.sum()),
            "n":         len(s),
        }

    def top_productos_ingreso(self, n: int = 10) -> pd.Series:
        """Top N productos por ingreso total."""
        return self._agrupar("producto", "total", head=n)

    def ticket_promedio_por_categoria(self) -> pd.Series:
        """Ticket promedio (total / nro de ventas) por categoría."""
        return self._agrupar("categoria", "total", func="mean")

    # ════════════════════════════════════════════════════════════
    # MÉTRICAS NUEVAS — DEMOGRÁFICAS
    # ════════════════════════════════════════════════════════════

    def ventas_por_genero(self) -> pd.Series:
        """Total vendido por género."""
        return self._agrupar("genero", "total")

    def unidades_por_genero(self) -> pd.Series:
        return self._agrupar("genero", "cantidad")

    def distribucion_edad(self) -> Dict[str, Any]:
        """Estadísticas de la distribución de edad de clientes."""
        if not self._tiene("edad"):
            return {}
        edades = self.df["edad"].dropna()
        if edades.empty:
            return {}
        return {
            "media":   float(edades.mean()),
            "mediana": float(edades.median()),
            "min":     int(edades.min()),
            "max":     int(edades.max()),
            "std":     float(edades.std()),
        }

    def ventas_por_grupo_edad(self) -> pd.Series:
        """Ventas agrupadas en rangos etarios."""
        if not self._tiene("edad"):
            return pd.Series(dtype=float)
        bins   = [0, 18, 25, 35, 45, 55, 65, 120]
        labels = ["<18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        col = pd.cut(self.df["edad"], bins=bins, labels=labels, right=False)
        return self.df.groupby(col, observed=False)["total"].sum()

    def top_ubicaciones(self, n: int = 10) -> pd.Series:
        """Top N estados/ciudades por volumen de ventas."""
        return self._agrupar("ubicacion", "total", head=n)

    def ventas_por_ubicacion(self) -> pd.Series:
        """Total de ventas por cada ubicación."""
        return self._agrupar("ubicacion", "total")

    # ════════════════════════════════════════════════════════════
    # MÉTRICAS NUEVAS — TRANSACCIONALES
    # ════════════════════════════════════════════════════════════

    def ventas_por_metodo_pago(self) -> pd.Series:
        return self._agrupar("metodo_pago", "total")

    def uso_descuentos(self) -> Dict[str, Any]:
        """Porcentaje de ventas con descuento y diferencia de ticket promedio."""
        if not self._tiene("descuento"):
            return {}
        con    = self.df[self.df["descuento"] == True]["total"]
        sin    = self.df[self.df["descuento"] == False]["total"]
        total  = len(self.df)
        return {
            "pct_con_descuento":    round(len(con) / total * 100, 2) if total else 0,
            "ticket_con_descuento": float(con.mean()) if len(con) else 0.0,
            "ticket_sin_descuento": float(sin.mean()) if len(sin) else 0.0,
            "n_con_descuento":      len(con),
            "n_sin_descuento":      len(sin),
        }

    def impacto_codigo_promo(self) -> Dict[str, Any]:
        """Diferencia de ticket con/sin código promocional."""
        if not self._tiene("codigo_promo"):
            return {}
        con = self.df[self.df["codigo_promo"] == True]["total"]
        sin = self.df[self.df["codigo_promo"] == False]["total"]
        total = len(self.df)
        return {
            "pct_uso_promo":    round(len(con) / total * 100, 2) if total else 0,
            "ticket_con_promo": float(con.mean()) if len(con) else 0.0,
            "ticket_sin_promo": float(sin.mean()) if len(sin) else 0.0,
        }

    def ventas_por_tipo_envio(self) -> pd.Series:
        return self._agrupar("tipo_envio", "total")

    # ════════════════════════════════════════════════════════════
    # MÉTRICAS NUEVAS — CALIDAD / FIDELIZACIÓN
    # ════════════════════════════════════════════════════════════

    def calificacion_promedio_por_producto(self) -> pd.Series:
        if not self._tiene("calificacion"):
            return pd.Series(dtype=float)
        return self._agrupar("producto", "calificacion", func="mean", filter_mask=(self.df["calificacion"] > 0))

    def calificacion_promedio_por_categoria(self) -> pd.Series:
        if not self._tiene("calificacion"):
            return pd.Series(dtype=float)
        return self._agrupar("categoria", "calificacion", func="mean", filter_mask=(self.df["calificacion"] > 0))

    def distribucion_calificaciones(self) -> pd.Series:
        """Conteo de reseñas por estrella (1–5)."""
        if not self._tiene("calificacion"):
            return pd.Series(dtype=int)
        return (
            self.df[self.df["calificacion"] > 0]["calificacion"]
            .round()
            .value_counts()
            .sort_index()
        )

    def ventas_por_frecuencia(self) -> pd.Series:
        return self._agrupar("frecuencia_compra", "total")

    def clientes_recurrentes_vs_nuevos(self) -> Dict[str, Any]:
        """Clientes con compras previas > 0 vs. nuevos."""
        if not self._tiene("compras_previas"):
            return {}
        recurrentes = self.df[self.df["compras_previas"] > 0]
        nuevos      = self.df[self.df["compras_previas"] == 0]
        total       = len(self.df)
        return {
            "pct_recurrentes": round(len(recurrentes) / total * 100, 2) if total else 0,
            "ticket_recurrente": float(recurrentes["total"].mean()) if len(recurrentes) else 0.0,
            "ticket_nuevo":      float(nuevos["total"].mean()) if len(nuevos) else 0.0,
            "n_recurrentes": len(recurrentes),
            "n_nuevos":      len(nuevos),
        }

    # ════════════════════════════════════════════════════════════
    # CORRELACIONES
    # ════════════════════════════════════════════════════════════

    def correlacion_edad_gasto(self) -> float:
        """Correlación de Pearson entre edad y monto gastado."""
        return self._correlacion("edad", "total")

    def correlacion_compras_previas_gasto(self) -> float:
        """Correlación entre historial de compras previas y ticket actual."""
        return self._correlacion("compras_previas", "total")

    def correlacion_calificacion_gasto(self) -> float:
        """Correlación entre calificación del producto y gasto."""
        if not self._tiene("calificacion"):
            return float("nan")
        sub = self.df[self.df["calificacion"] > 0][["calificacion", "total"]].dropna()
        if len(sub) < 2:
            return float("nan")
        return float(np.corrcoef(sub["calificacion"], sub["total"])[0, 1])

    # ════════════════════════════════════════════════════════════
    # RESUMEN COMPLETO
    # ════════════════════════════════════════════════════════════

    def resumen_general(self, imprimir: bool = True) -> Dict[str, Any]:
        stats   = self.estadisticas_precio()
        desc_info = self.uso_descuentos()
        promo_info = self.impacto_codigo_promo()
        fid_info = self.clientes_recurrentes_vs_nuevos()

        resumen: Dict[str, Any] = {
            # Originales
            "total_ventas":                  stats.get("total", 0.0),
            "producto_mas_vendido":          self.producto_mas_vendido(),
            "producto_menos_demandado":      self.producto_menos_demanda(),
            "ingreso_promedio_por_venta":    stats.get("media", 0.0),
            "ingreso_promedio_por_producto": self.ingreso_promedio_por_producto(),
            "ventas_por_categoria":          self.ventas_por_categoria(),
            "ventas_por_temporada":          self.ventas_por_temporada(),
            "unidades_por_categoria":        self.unidades_por_categoria(),
            # Nuevas
            "estadisticas_precio":           stats,
            "top_productos_ingreso":         self.top_productos_ingreso(),
            "ticket_por_categoria":          self.ticket_promedio_por_categoria(),
            "ventas_por_genero":             self.ventas_por_genero(),
            "distribucion_edad":             self.distribucion_edad(),
            "ventas_por_grupo_edad":         self.ventas_por_grupo_edad(),
            "top_ubicaciones":              self.top_ubicaciones(),
            "ventas_por_metodo_pago":        self.ventas_por_metodo_pago(),
            "uso_descuentos":                desc_info,
            "impacto_codigo_promo":          promo_info,
            "ventas_por_tipo_envio":         self.ventas_por_tipo_envio(),
            "calificacion_por_categoria":    self.calificacion_promedio_por_categoria(),
            "ventas_por_frecuencia":         self.ventas_por_frecuencia(),
            "fidelizacion":                  fid_info,
            "corr_edad_gasto":               self.correlacion_edad_gasto(),
            "corr_compras_gasto":            self.correlacion_compras_previas_gasto(),
            "corr_calificacion_gasto":       self.correlacion_calificacion_gasto(),
        }

        if imprimir and stats:
            print(f"Total ventas:            ${stats['total']:,.2f}")
            print(f"Ticket promedio:         ${stats['media']:,.2f}")
            print(f"Desv. estándar:          ${stats['std']:,.2f}")
            print(f"Rango IQR:               ${stats['rango_iqr']:,.2f}")
            if desc_info:
                print(f"% con descuento:         {desc_info['pct_con_descuento']}%")
            if fid_info:
                print(f"% clientes recurrentes:  {fid_info['pct_recurrentes']}%")
            r = self.correlacion_edad_gasto()
            if not np.isnan(r):
                print(f"Corr. edad↔gasto:        {r:.3f}")

        return resumen
