import matplotlib.pyplot as plt

REGION_COL = "World region according to OWID"


def guardar_grafico(nombre, carpeta, mostrar):
    plt.tight_layout()
    plt.savefig(carpeta / nombre, dpi=120)
    if mostrar:
        plt.show()
    plt.close()


def graficar(datos, vida, anio, carpeta, mostrar=False):
    """Guarda dispersión, histograma, cajas y evolución de países."""
    carpeta.mkdir(parents=True, exist_ok=True)
    # Dispersión: esperanza de vida, PIB y CO₂ representado por color.
    plt.figure(figsize=(9, 6))
    puntos = plt.scatter(datos["Life expectancy"], datos["GDP per capita"],
                         c=datos["CO₂ emissions per capita"], cmap="viridis", alpha=0.6)
    plt.colorbar(puntos, label="CO₂ por habitante")
    plt.xlabel("Esperanza de vida (años)")
    plt.ylabel("PIB por habitante (escala logarítmica)")
    plt.yscale("log")
    plt.title(f"Esperanza de vida y PIB — {anio}")
    guardar_grafico(f"dispersion_{anio}.png", carpeta, mostrar)

    # Histograma: distribución de la esperanza de vida.
    plt.figure(figsize=(9, 5))
    plt.hist(datos["Life expectancy"], bins=12, color="teal", edgecolor="white")
    plt.xlabel("Esperanza de vida (años)")
    plt.ylabel("Cantidad de países y territorios")
    plt.title(f"Distribución de esperanza de vida — {anio}")
    guardar_grafico(f"histograma_{anio}.png", carpeta, mostrar)

    # Cajas: comparación de regiones.
    grupos = list(datos.groupby(REGION_COL)["Life expectancy"])
    plt.figure(figsize=(11, 6))
    plt.boxplot([valores.to_numpy() for _, valores in grupos])
    plt.xticks(range(1, len(grupos) + 1), [region for region, _ in grupos], rotation=20)
    plt.ylabel("Esperanza de vida (años)")
    plt.title(f"Esperanza de vida por región — {anio}")
    guardar_grafico(f"regiones_{anio}.png", carpeta, mostrar)

    # Líneas: evolución de cuatro países desde 1990.
    paises = {"CHL": "Chile", "ARG": "Argentina", "BRA": "Brasil", "PER": "Perú"}
    seleccion = vida[vida["Code"].isin(paises) & vida["Year"].between(1990, anio)]
    if not seleccion.empty:
        tabla = seleccion.pivot(index="Year", columns="Code", values="Life expectancy")
        tabla = tabla.sort_index().rename(columns=paises)
        tabla.plot(figsize=(10, 6))
        plt.xlabel("Año")
        plt.ylabel("Esperanza de vida (años)")
        plt.title(f"Esperanza de vida en países seleccionados — 1990–{anio}")
        guardar_grafico(f"evolucion_{anio}.png", carpeta, mostrar)
