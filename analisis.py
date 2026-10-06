VARIABLES = ["Life expectancy", "GDP per capita", "CO₂ emissions per capita"]


def analizar(unidos, anio, salida):
    """Selecciona un año, muestra estadísticas y guarda las tablas."""
    datos = unidos[unidos["Year"] == anio].copy()
    if datos.empty:
        raise ValueError(f"No hay datos coincidentes para {anio}.")
    resumen = datos[VARIABLES].agg(["count", "mean", "min", "max"]).T
    resumen.columns = ["Cantidad", "Promedio", "Mínimo", "Máximo"]
    correlaciones = datos[VARIABLES].corr()
    print("Países y territorios:", datos["Code"].nunique())
    print("\nResumen:\n", resumen.round(2))
    print("\nCorrelaciones:\n", correlaciones.round(2))
    print("\nCinco países con mayor esperanza de vida:\n",
          datos.nlargest(5, "Life expectancy")[["Entity", "Life expectancy"]])
    datos.to_csv(salida / f"merged_{anio}.csv", index=False)
    resumen.to_csv(salida / f"resumen_{anio}.csv")
    correlaciones.to_csv(salida / f"correlaciones_{anio}.csv")
    return datos
