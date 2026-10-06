import numpy as np
import pandas as pd

CLAVES = ["Entity", "Code", "Year"]
REGION_COL = "World region according to OWID"


def limpiar(datos_originales, indicador):
    """Limpia una fuente y aplica la regla del 5 % a su indicador numérico."""
    columnas = CLAVES + [indicador]
    if REGION_COL in datos_originales.columns:
        columnas.append(REGION_COL)
    datos = datos_originales[columnas].copy()

    for columna in ["Entity", "Code", REGION_COL]:
        if columna in datos.columns:
            datos[columna] = datos[columna].astype("string").str.strip().replace("", pd.NA)

    datos["Year"] = pd.to_numeric(datos["Year"], errors="coerce")
    # Las claves identifican cada registro: no se pueden promediar.
    datos = datos.dropna(subset=CLAVES)
    datos = datos[np.isfinite(datos["Year"]) & (datos["Year"] % 1 == 0)].copy()
    es_pais = datos["Code"].str.fullmatch(r"[A-Z]{3}", na=False) | datos["Code"].eq("OWID_KOS")
    datos = datos[es_pais].drop_duplicates(subset=["Code", "Year"]).copy()
    if datos.empty:
        raise ValueError(f"No hay registros de países válidos en {indicador}.")
    datos["Year"] = datos["Year"].astype(int)

    datos[indicador] = pd.to_numeric(datos[indicador], errors="coerce")
    invalidos = ~np.isfinite(datos[indicador])
    if indicador == "CO₂ emissions per capita":
        invalidos |= datos[indicador] < 0
    else:
        invalidos |= datos[indicador] <= 0
    datos.loc[invalidos, indicador] = np.nan

    cantidad = int(datos[indicador].isna().sum())
    porcentaje = cantidad / len(datos) * 100
    if porcentaje > 5:
        promedio = datos[indicador].mean()
        if pd.isna(promedio):
            raise ValueError(f"No hay valores válidos para calcular el promedio de {indicador}.")
        datos[indicador] = datos[indicador].fillna(promedio)
        accion = f"completados con el promedio ({promedio:.2f})"
    else:
        datos = datos.dropna(subset=[indicador]).copy()
        accion = "eliminados"
    print(f"{indicador}: {cantidad} inválidos o nulos ({porcentaje:.2f} %), {accion}. Quedan {len(datos)} filas.")

    if REGION_COL in datos.columns:
        datos[REGION_COL] = datos[REGION_COL].fillna("Sin región")
    return datos

