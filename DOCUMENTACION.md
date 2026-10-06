# Documentación del programa

## Objetivo

Comparar la esperanza de vida, el PIB por habitante y las emisiones de CO₂ por habitante usando tres archivos CSV. El programa tiene cuatro partes: **limpieza, unión, análisis y gráficos**. Los resultados se presentan en un dashboard HTML.

## Organización del código

| Archivo | Función principal | Qué hace |
| --- | --- | --- |
| `main.py` | — | Inicia el programa llamando a `ejecutar()`. |
| `controlador.py` | `ejecutar()` | Lee los archivos y coordina las cuatro partes. Contiene el año, las rutas y la opción para mostrar gráficos. |
| `limpieza.py` | `limpiar()` | Limpia cada fuente y aplica la regla del 5 %. |
| `union.py` | `unir()` | Une los registros que coinciden en las tres fuentes. |
| `analisis.py` | `analizar()` | Selecciona el año, calcula estadísticas y guarda las tablas. |
| `graficos.py` | `graficar()` | Genera hasta cuatro gráficos. `guardar_grafico()` guarda cada imagen. |
| `dashboard.py` | `crear_dashboard()` | Crea el informe HTML con indicadores, figuras y una tabla de resultados. |

El recorrido del programa es:

```text
main.py → controlador.py
              1. limpieza.py
              2. union.py
              3. analisis.py
              4. graficos.py → dashboard.py
```

El dashboard presenta los resultados de la cuarta parte; no agrega otra etapa de análisis.

## Datos y ejecución

Los originales se encuentran en `data/input/`:

| Archivo | Indicador |
| --- | --- |
| `co-emissions-per-capita.csv` | Emisiones de CO₂ por habitante. |
| `gdp-per-capita-worldbank.csv` | PIB por habitante; también contiene la región. |
| `life-expectancy.csv` | Esperanza de vida en años. |

Se usan pandas para leer y trabajar con tablas, NumPy para identificar valores numéricos inválidos y Matplotlib para los gráficos. El dashboard usa herramientas incluidas en Python, sin dependencias adicionales.

Desde la carpeta del proyecto:

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

Al principio de `controlador.py` se pueden cambiar:

- `ANIO = 2023`: año del análisis.
- `MOSTRAR_GRAFICOS = False`: guarda las imágenes sin abrir ventanas. Con `True`, también las muestra.

Los CSV originales no se modifican. Los resultados se guardan en `data/processed/`. Si se elimina esa carpeta, el programa vuelve a crearla al ejecutarse.

## 1. Limpieza

`limpiar(datos_originales, indicador)` recibe una tabla y el nombre del indicador. Devuelve una copia limpia.

Primero quita espacios de los textos, reconoce cadenas vacías como nulos y convierte el año y el indicador a números. Los textos no numéricos se convierten en nulos mediante `pd.to_numeric(..., errors="coerce")`.

Luego elimina filas sin país, código o año, años no enteros o infinitos y entidades agregadas, como continentes. Conserva códigos de tres letras y Kosovo (`OWID_KOS`). Para duplicados de código y año, conserva la primera fila.

Los indicadores se validan así:

| Indicador | Valores inválidos |
| --- | --- |
| Esperanza de vida | Nulos, no numéricos, infinitos o menores o iguales a cero. |
| PIB por habitante | Nulos, no numéricos, infinitos o menores o iguales a cero. |
| CO₂ por habitante | Nulos, no numéricos, infinitos o negativos. Cero es válido. |

### Regla del 5 %

```text
porcentaje = cantidad de valores inválidos o nulos / cantidad de filas × 100
```

- **Más del 5 %:** completa los valores inválidos o nulos con el promedio de los valores válidos del indicador.
- **5 % o menos:** elimina las filas afectadas.

Por ejemplo, en 100 registros, 6 valores nulos se completan con el promedio; 5 valores nulos provocan la eliminación de esas 5 filas.

El porcentaje se calcula por indicador y por fuente, después de filtrar identificadores y duplicados, antes de unir los archivos. El promedio usa todos los países y años válidos de esa fuente. Si no hay valores válidos para calcularlo, el programa muestra un error.

Los identificadores no se completan con promedios: si faltan, se elimina la fila. Una región faltante recibe la etiqueta `Sin región`, porque es una categoría de texto.

## 2. Unión

`unir(co2, pib, vida)` usa `merge()` con estas tres claves:

- `Entity`: nombre del país o territorio.
- `Code`: código.
- `Year`: año.

`how="inner"` conserva solamente las coincidencias en las tres fuentes. `validate="one_to_one"` comprueba que las claves de unión sean únicas.

**¿Por qué algunos registros no se unen?** Las fuentes pueden cubrir distintos países y años. Por ejemplo, si Chile tiene CO₂ y esperanza de vida para un año, pero falta su PIB, ese registro queda fuera. También se requiere que el nombre coincida exactamente, además del código y año. Las filas eliminadas durante la limpieza tampoco participan en la unión.

La tabla se guarda en `merged_all.csv`. Los **6.488 registros unidos** de los datos actuales corresponden a todos los años disponibles, no solo a 2023.

## 3. Análisis

`analizar(unidos, anio, salida)` selecciona el año configurado. Si no hay coincidencias para ese año, muestra un error.

Calcula cantidad de registros, promedio, mínimo y máximo de cada indicador; correlaciones de Pearson entre las tres variables; y los cinco países o territorios con mayor esperanza de vida.

Con los archivos actuales, para 2023:

| Resultado | Valor aproximado |
| --- | --- |
| Países y territorios analizados | 194 |
| Esperanza de vida promedio | 73,32 años |
| PIB por habitante promedio | 26.831,76 |
| CO₂ por habitante promedio | 4,60 |
| Correlación entre esperanza de vida y PIB | 0,74 |

Los promedios son simples entre países y territorios, sin ponderar por población. Las unidades de PIB y CO₂ se conservan según los CSV originales. En las fuentes filtradas actuales no hubo valores de indicadores que requirieran completar con el promedio.

Una correlación cercana a 1 indica asociación positiva, cercana a −1 asociación negativa y cercana a 0 poca asociación lineal. El valor 0,74 indica que, en esta muestra, los países con mayor PIB tienden a tener mayor esperanza de vida. Esto no demuestra causalidad. La cobertura de las fuentes y completar valores con promedios pueden influir en los resultados.

## 4. Gráficos y dashboard

`graficar()` genera como máximo cuatro imágenes en `data/processed/figures/`:

| Gráfico | Archivo para 2023 | Qué permite observar |
| --- | --- | --- |
| Dispersión | `dispersion_2023.png` | Esperanza de vida frente a PIB; el color representa CO₂. El PIB usa escala logarítmica. |
| Histograma | `histograma_2023.png` | Cantidad de países y territorios en cada intervalo de esperanza de vida. |
| Cajas por región | `regiones_2023.png` | Mediana y dispersión de la esperanza de vida en cada región. |
| Evolución | `evolucion_2023.png` | Esperanza de vida en Chile, Argentina, Brasil y Perú desde 1990 hasta el año seleccionado. |

Los primeros tres usan la tabla unida del año seleccionado. La evolución usa la fuente limpia de esperanza de vida y se genera si existen registros de esos países en el período.

Después, `crear_dashboard()` crea `data/processed/dashboard/index.html`. Para presentarlo, abre ese archivo en un navegador. El informe muestra:

- Cantidad de países y territorios y esperanza de vida promedio.
- Medianas de PIB y CO₂ por habitante.
- Las figuras disponibles, que se pueden seleccionar para abrir en tamaño completo.
- Una tabla con los cinco países o territorios con mayor esperanza de vida.
- Una explicación breve de los resultados y del tratamiento de datos.

**Promedio y mediana:** el promedio suma los valores y los divide por su cantidad; la mediana es el valor central de los datos ordenados. El resumen CSV contiene promedios; el dashboard utiliza medianas para PIB y CO₂, como indican sus etiquetas.

Los números del dashboard se redondean para facilitar la lectura. Por ejemplo, `85,5` significa 85,5 años de esperanza de vida, no un porcentaje.

El HTML se actualiza al ejecutar el programa. Sus imágenes usan rutas relativas: si copias el informe, conserva juntas las carpetas `dashboard/` y `figures/` dentro de la misma carpeta.

## Archivos generados

```text
data/processed/
├── merged_all.csv          # Unión de todos los años
├── merged_2023.csv         # Datos del año seleccionado
├── resumen_2023.csv        # Estadísticas básicas
├── correlaciones_2023.csv  # Correlaciones
├── figures/               # Hasta cuatro imágenes PNG
└── dashboard/
    └── index.html         # Informe para presentar
```

Los nombres que incluyen 2023 cambian si se modifica `ANIO`. Los archivos de ejecuciones de otros años permanecen hasta que se eliminen manualmente.

## Guion breve para presentar

> Nuestro programa compara esperanza de vida, PIB y emisiones de CO₂. El controlador carga tres archivos y organiza cuatro partes.
>
> Primero limpiamos los datos. Cuando los valores inválidos o nulos superan el 5 %, los completamos con el promedio; cuando son el 5 % o menos, eliminamos esas filas.
>
> Después unimos por país, código y año. Conservamos solo las coincidencias de las tres fuentes, por eso algunos registros quedan fuera.
>
> Luego analizamos 2023. Tenemos 194 países y territorios y calculamos estadísticas básicas y correlaciones. La asociación entre PIB y esperanza de vida es positiva, pero no demuestra causalidad.
>
> Finalmente mostramos cuatro gráficos y el dashboard, que reúne las figuras y los resultados principales.

Para explicar el código, muestra `main.py`, luego `controlador.py` y después los archivos en el orden de las cuatro partes. Termina abriendo el dashboard.

## Verificación realizada

Se comprobó la ejecución completa con los tres CSV originales, la generación de cuatro tablas y cuatro imágenes, y la existencia de las cuatro rutas de imágenes del dashboard. También se comprobó la limpieza con casos menores, iguales y mayores al 5 %, ausencia de valores válidos y CO₂ igual a cero.
