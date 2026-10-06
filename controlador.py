from pathlib import Path
import pandas as pd

from limpieza import limpiar
from union import unir
from analisis import analizar
from graficos import graficar
from dashboard import crear_dashboard

# Parámetros que se pueden cambiar para la presentación.
ANIO = 2023
MOSTRAR_GRAFICOS = False
CARPETA = Path(__file__).resolve().parent
ENTRADA = CARPETA / "data" / "input"
SALIDA = CARPETA / "data" / "processed"


def ejecutar():
    """Carga los archivos y coordina las cuatro partes del programa."""
    SALIDA.mkdir(parents=True, exist_ok=True)
    co2 = pd.read_csv(ENTRADA / "co-emissions-per-capita.csv")
    pib = pd.read_csv(ENTRADA / "gdp-per-capita-worldbank.csv")
    vida = pd.read_csv(ENTRADA / "life-expectancy.csv")

    print("\n1. LIMPIEZA")
    co2 = limpiar(co2, "CO₂ emissions per capita")
    pib = limpiar(pib, "GDP per capita")
    vida = limpiar(vida, "Life expectancy")

    print("\n2. UNIÓN")
    unidos = unir(co2, pib, vida)
    unidos.to_csv(SALIDA / "merged_all.csv", index=False)
    print("Registros unidos:", len(unidos))

    print(f"\n3. ANÁLISIS ({ANIO})")
    datos = analizar(unidos, ANIO, SALIDA)

    print("\n4. GRÁFICOS")
    graficar(datos, vida, ANIO, SALIDA / "figures", MOSTRAR_GRAFICOS)
    dashboard = crear_dashboard(datos, ANIO, SALIDA)
    print("Dashboard:", dashboard)
    print("Resultados guardados en:", SALIDA)
