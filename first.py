"""Preparación, unión y exploración de los datos con cuatro gráficos."""
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

# 1. Cargar los CSV
co2 = pd.read_csv("co-emissions-per-capita.csv")
pib = pd.read_csv("gdp-per-capita-worldbank.csv")
exp = pd.read_csv("life-expectancy.csv")
claves = ["Entity", "Code", "Year"]
variables = ["Life expectancy", "GDP per capita", "CO₂ emissions per capita"]
anio = 2023

# La regla del material exige <5 %, ausencia completamente aleatoria y sin sesgo.
# Python mide el porcentaje, pero no demuestra las otras dos condiciones.
def revisar_faltantes(datos, columnas):
    if datos.empty:
        raise ValueError("La selección está vacía; revisar filtros y coincidencias.")
    incompletas = datos[columnas].isna().any(axis=1)
    cantidad = int(incompletas.sum())
    porcentaje = incompletas.mean() * 100
    print(f"Filas incompletas en {columnas}: {cantidad}/{len(datos)} ({porcentaje:.2f} %)")
    if cantidad:
        print("Ejemplos para revisar:\n", datos.loc[incompletas].head(10).to_string(index=False))
        if porcentaje >= 5:
            raise ValueError("Se alcanza o supera el 5 %: evaluar otro tratamiento.")
        raise ValueError("Menos del 5 %: investigar el patrón y justificar antes de eliminar.")

# 2. Aplicar las mismas reglas a cada fuente sin modificar los CSV originales.
def preparar_fuente(df, indicador):
    datos = df.copy()
    # Unificar espacios en identificadores y reconocer cadenas vacías como faltantes.
    for columna in ["Entity", "Code", "World region according to OWID"]:
        if columna in datos.columns:
            datos[columna] = datos[columna].astype("string").str.strip().replace("", pd.NA)
    print(f"\n{indicador}: {len(datos)} filas originales")
    print("Faltantes originales:\n", datos[claves + [indicador]].isna().sum())
    for columna in ["Year", indicador]:
        original = datos[columna]
        datos[columna] = pd.to_numeric(original, errors="coerce")
        print(f"No numéricos en {columna}:",
              int((original.notna() & datos[columna].isna()).sum()))
    if (datos["Year"].dropna() % 1 != 0).any():
        raise ValueError("Hay años no enteros; revisar la fuente.")

    # Seleccionar países y territorios según sus códigos, incluido Kosovo.
    # Esta selección de entidades es distinta de eliminar filas por faltantes.
    es_pais = datos["Code"].str.fullmatch(r"[A-Z]{3}", na=False)
    es_pais = es_pais | datos["Code"].eq("OWID_KOS")
    print("Filas fuera del criterio de entidades:", int((~es_pais).sum()))
    datos = datos[es_pais].copy()
    revisar_faltantes(datos, claves)
    if datos.duplicated(["Code", "Year"]).any():
        raise ValueError("Hay claves país-año repetidas; revisar la fuente.")

    # CO₂ admite cero; PIB y esperanza de vida deben ser positivos aquí.
    invalidos = datos[indicador] < 0 if indicador == variables[2] else datos[indicador] <= 0
    print("Valores no válidos para este análisis:", int(invalidos.sum()))
    datos.loc[invalidos, indicador] = float("nan")
    print("Filas preparadas:", len(datos))
    return datos

co2_limpio = preparar_fuente(co2, variables[2])
pib_limpio = preparar_fuente(pib, variables[1])
exp_limpio = preparar_fuente(exp, variables[0])

# 3. Unir el mismo país y año. inner conserva coincidencias; validate evita duplicados.
merge = pd.merge(co2_limpio, pib_limpio, on=claves, how="inner", validate="one_to_one")
resultado = pd.merge(merge, exp_limpio, on=claves, how="inner", validate="one_to_one")
print("\nFilas antes y después de unir:", len(co2_limpio), "→", len(merge), "→", len(resultado))
print("inner conserva coincidencias país-año; estas reducciones no son eliminación por N/A.")

# 4. Revisar el porcentaje ANTES de decidir el tratamiento de los faltantes.
resultado2023 = resultado[resultado["Year"] == anio].copy()
print(f"\nFaltantes en {anio}:\n", resultado2023[variables].isna().sum())
revisar_faltantes(resultado2023, variables)
# Con estos archivos hay 0 % de filas incompletas: no hace falta eliminar ni imputar.
print("Observaciones completas:", len(resultado2023))
print(resultado2023.head(10).to_string(index=False))

# 5. Dispersión: X = esperanza de vida, Y = PIB, color = CO₂.
fig, ax = plt.subplots(figsize=(9, 6))
puntos = ax.scatter(
    resultado2023["Life expectancy"], resultado2023["GDP per capita"],
    c=resultado2023["CO₂ emissions per capita"], cmap="viridis", alpha=0.6, s=40
)
fig.colorbar(puntos, ax=ax, label="Emisiones de CO₂ por habitante")
ax.set_title(f"Esperanza de vida y PIB por habitante — {anio}")
ax.set_xlabel("Esperanza de vida (años)")
ax.set_ylabel("PIB por habitante (escala logarítmica)")
ax.set_yscale("log")
ax.grid(alpha=0.2)
ax.set_axisbelow(True)
fig.tight_layout()

# 6. Histograma: contar países y territorios por intervalos de esperanza de vida.
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(resultado2023["Life expectancy"], bins=12, edgecolor="white", color="teal")
ax.set_title(f"Distribución de la esperanza de vida — {anio}")
ax.set(xlabel="Esperanza de vida (años)", ylabel="Cantidad de países y territorios")
ax.grid(axis="y", alpha=0.2)
ax.set_axisbelow(True)
fig.tight_layout()

# 7. Cajas: comparar mediana y dispersión por región; los extremos no se eliminan.
region = "World region according to OWID"
revisar_faltantes(resultado2023, [region])
datos_cajas = resultado2023
grupos = list(datos_cajas.groupby(region)["Life expectancy"])
fig, ax = plt.subplots(figsize=(11, 6))
ax.boxplot([valores.to_numpy() for nombre, valores in grupos])
ax.set_xticks(range(1, len(grupos) + 1))
ax.set_xticklabels([nombre for nombre, valores in grupos], rotation=20, ha="right")
ax.set_title(f"Esperanza de vida por región — {anio}")
ax.set_ylabel("Esperanza de vida (años)")
ax.grid(axis="y", alpha=0.2)
ax.set_axisbelow(True)
fig.tight_layout()

# 8. Líneas: usar la fuente de esperanza de vida, sin exigir coincidencias con PIB o CO₂.
paises = {"CHL": "Chile", "ARG": "Argentina", "BRA": "Brasil", "PER": "Perú"}
series = exp_limpio[
    exp_limpio["Code"].isin(paises) & exp_limpio["Year"].between(1990, anio)
]
revisar_faltantes(series, ["Life expectancy"])
tabla = series.pivot(index="Year", columns="Code", values="Life expectancy")
tabla = tabla.sort_index().rename(columns=paises)
fig, ax = plt.subplots(figsize=(10, 6))
tabla.plot(ax=ax, linewidth=2)
ax.set_title(f"Esperanza de vida en países seleccionados — 1990–{anio}")
ax.set(xlabel="Año", ylabel="Esperanza de vida (años)")
ax.legend(title="País")
ax.grid(alpha=0.2)
fig.tight_layout()

# Verificar las unidades de PIB y CO₂ en los metadatos antes de entregar.
# Estos gráficos exploran asociaciones; no demuestran causalidad.
plt.show()
