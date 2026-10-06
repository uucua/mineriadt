# Minería de datos

Análisis de esperanza de vida, PIB y CO₂ en cuatro partes: limpieza, unión, análisis y gráficos.

`main.py` inicia el programa. `controlador.py` coordina `limpieza.py`, `union.py`, `analisis.py` y `graficos.py`; después genera el informe con `dashboard.py`.

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

Los originales están en `data/input/`. Los resultados se crean en `data/processed/`. Para presentar, abre `data/processed/dashboard/index.html` en un navegador.

Consulta [DOCUMENTACION.md](DOCUMENTACION.md) para la explicación del código, la regla del 5 %, los resultados y el guion de presentación.
