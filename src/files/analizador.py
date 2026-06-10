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
    # MÉTRICAS ORIGINALES
    # ════════════════════════════════════════════════════════════

    def total_ventas(self) -> float:
        return float(self.df["total"].sum()) if not self.df.empty else 0.0

    def producto_mas_vendido(self) -> pd.Series:
        return self.df.groupby("producto")["cantidad"].sum().sort_values(ascending=False).head(1)

    def producto_menos_demanda(self) -> pd.Series:
        return self.df.groupby("producto")["cantidad"].sum().sort_values().head(1)

    def ingreso_promedio_por_venta(self) -> float:
        return float(self.df["total"].mean()) if not self.df.empty else 0.0

    def ingreso_promedio_por_producto(self) -> pd.Series:
        return self.df.groupby("producto")["total"].mean().sort_values(ascending=False)

    def ventas_por_categoria(self) -> pd.Series:
        return self.df.groupby("categoria")["total"].sum().sort_values(ascending=False)

    def unidades_por_categoria(self) -> pd.Series:
        return self.df.groupby("categoria")["cantidad"].sum().sort_values(ascending=False)

    def ventas_por_temporada(self) -> pd.Series:
        return self.df.groupby("temporada")["total"].sum().sort_values(ascending=False)

    # ════════════════════════════════════════════════════════════
    # MÉTRICAS NUEVAS — ESTADÍSTICAS DESCRIPTIVAS
    # ════════════════════════════════════════════════════════════

    def estadisticas_precio(self) -> Dict[str, float]:
        """Media, mediana, desv. estándar, percentil 25/75 y rango del precio."""
        s = self.df["total"]
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
        return self.df.groupby("producto")["total"].sum().sort_values(ascending=False).head(n)

    def ticket_promedio_por_categoria(self) -> pd.Series:
        """Ticket promedio (total / nro de ventas) por categoría."""
        return self.df.groupby("categoria")["total"].mean().sort_values(ascending=False)

    # ════════════════════════════════════════════════════════════
    # MÉTRICAS NUEVAS — DEMOGRÁFICAS
    # ════════════════════════════════════════════════════════════

    def ventas_por_genero(self) -> pd.Series:
        """Total vendido por género."""
        if not self._tiene("genero"):
            return pd.Series(dtype=float)
        return self.df.groupby("genero")["total"].sum().sort_values(ascending=False)

    def unidades_por_genero(self) -> pd.Series:
        if not self._tiene("genero"):
            return pd.Series(dtype=float)
        return self.df.groupby("genero")["cantidad"].sum().sort_values(ascending=False)

    def distribucion_edad(self) -> Dict[str, Any]:
        """Estadísticas de la distribución de edad de clientes."""
        if not self._tiene("edad"):
            return {}
        edades = self.df["edad"].dropna()
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
        if not self._tiene("ubicacion"):
            return pd.Series(dtype=float)
        return self.df.groupby("ubicacion")["total"].sum().sort_values(ascending=False).head(n)

    def ventas_por_ubicacion(self) -> pd.Series:
        """Total de ventas por cada ubicación."""
        if not self._tiene("ubicacion"):
            return pd.Series(dtype=float)
        return self.df.groupby("ubicacion")["total"].sum().sort_values(ascending=False)

    # ════════════════════════════════════════════════════════════
    # MÉTRICAS NUEVAS — TRANSACCIONALES
    # ════════════════════════════════════════════════════════════

    def ventas_por_metodo_pago(self) -> pd.Series:
        if not self._tiene("metodo_pago"):
            return pd.Series(dtype=float)
        return self.df.groupby("metodo_pago")["total"].sum().sort_values(ascending=False)

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
        if not self._tiene("tipo_envio"):
            return pd.Series(dtype=float)
        return self.df.groupby("tipo_envio")["total"].sum().sort_values(ascending=False)

    # ════════════════════════════════════════════════════════════
    # MÉTRICAS NUEVAS — CALIDAD / FIDELIZACIÓN
    # ════════════════════════════════════════════════════════════

    def calificacion_promedio_por_producto(self) -> pd.Series:
        if not self._tiene("calificacion"):
            return pd.Series(dtype=float)
        return (
            self.df[self.df["calificacion"] > 0]
            .groupby("producto")["calificacion"]
            .mean()
            .sort_values(ascending=False)
        )

    def calificacion_promedio_por_categoria(self) -> pd.Series:
        if not self._tiene("calificacion"):
            return pd.Series(dtype=float)
        return (
            self.df[self.df["calificacion"] > 0]
            .groupby("categoria")["calificacion"]
            .mean()
            .sort_values(ascending=False)
        )

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
        if not self._tiene("frecuencia_compra"):
            return pd.Series(dtype=float)
        return self.df.groupby("frecuencia_compra")["total"].sum().sort_values(ascending=False)

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
        if not self._tiene("edad"):
            return float("nan")
        sub = self.df[["edad", "total"]].dropna()
        if len(sub) < 2:
            return float("nan")
        return float(np.corrcoef(sub["edad"], sub["total"])[0, 1])

    def correlacion_compras_previas_gasto(self) -> float:
        """Correlación entre historial de compras previas y ticket actual."""
        if not self._tiene("compras_previas"):
            return float("nan")
        sub = self.df[["compras_previas", "total"]].dropna()
        if len(sub) < 2:
            return float("nan")
        return float(np.corrcoef(sub["compras_previas"], sub["total"])[0, 1])

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
            "total_ventas":                  stats["total"],
            "producto_mas_vendido":          self.producto_mas_vendido(),
            "producto_menos_demandado":      self.producto_menos_demanda(),
            "ingreso_promedio_por_venta":    stats["media"],
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

        if imprimir:
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
