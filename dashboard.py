from html import escape


def crear_dashboard(datos, anio, salida):
    """Crea un informe HTML con los resultados y las figuras del programa."""
    carpeta = salida / "dashboard"
    carpeta.mkdir(parents=True, exist_ok=True)

    def numero(valor, decimales=1):
        return f"{valor:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")

    indicadores = [
        ("Países y territorios", str(datos["Code"].nunique()), "Con datos en las tres fuentes"),
        ("Esperanza de vida", numero(datos["Life expectancy"].mean()) + " años", "Promedio entre países"),
        ("PIB por habitante", numero(datos["GDP per capita"].median(), 0), "Mediana · unidades del archivo fuente"),
        ("CO₂ por habitante", numero(datos["CO₂ emissions per capita"].median(), 2), "Mediana · unidades del archivo fuente"),
    ]
    tarjetas = "".join(
        f'<div class="indicador"><dt>{titulo}</dt><dd>{valor}</dd><p>{detalle}</p></div>'
        for titulo, valor, detalle in indicadores
    )

    figuras = [
        ("dispersion", "Desarrollo y esperanza de vida", "El color representa las emisiones de CO₂ por habitante. El PIB se presenta en escala logarítmica."),
        ("histograma", "Distribución de la esperanza de vida", "Cantidad de países y territorios en cada intervalo de esperanza de vida."),
        ("regiones", "Diferencias entre regiones", "Las cajas muestran la mediana y la dispersión de la esperanza de vida de cada región."),
        ("evolucion", "Evolución en cuatro países", f"Chile, Argentina, Brasil y Perú, desde 1990 hasta {anio}."),
    ]
    graficos = ""
    for posicion, (nombre, titulo, detalle) in enumerate(figuras, start=1):
        archivo = f"{nombre}_{anio}.png"
        if not (salida / "figures" / archivo).exists():
            continue
        graficos += f'''<figure>
            <figcaption><span class="numero">{posicion:02}</span><div><h3>{titulo}</h3><p>{detalle}</p></div></figcaption>
            <a href="../figures/{archivo}" target="_blank" rel="noopener" aria-label="Ampliar: {titulo}">
                <img src="../figures/{archivo}" alt="{titulo}. {detalle}">
            </a>
        </figure>'''

    filas = ""
    for _, pais in datos.nlargest(5, "Life expectancy").iterrows():
        filas += f'<tr><td>{escape(str(pais["Entity"]))}</td><td>{escape(str(pais["World region according to OWID"]))}</td><td>{numero(pais["Life expectancy"])} años</td></tr>'
    correlacion = datos["Life expectancy"].corr(datos["GDP per capita"])
    html = '''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Salud, desarrollo y emisiones · __ANIO__</title>
<style>
:root { color-scheme: light; --tinta: #202d39; --gris: #5e6a74; --linea: #dce1e4; --azul: #234d67; }
* { box-sizing: border-box; }
body { margin: 0; background: #f5f6f6; color: var(--tinta); font-family: Arial, Helvetica, sans-serif; line-height: 1.55; }
.contenedor { max-width: 1240px; margin: auto; padding: 0 36px; }
header { background: white; border-top: 5px solid var(--azul); border-bottom: 1px solid var(--linea); padding: 38px 0 28px; }
.encabezado { display: flex; justify-content: space-between; align-items: flex-start; gap: 24px; }
.etiqueta { margin: 0 0 12px; color: var(--azul); font-size: 12px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; }
h1 { margin: 0; font-family: Georgia, serif; font-size: clamp(30px, 4vw, 44px); line-height: 1.15; font-weight: normal; }
.subtitulo { color: var(--gris); margin: 14px 0 0; max-width: 690px; }
.periodo { min-width: 100px; border-left: 1px solid var(--linea); padding-left: 24px; color: var(--gris); font-size: 12px; }
.periodo strong { display: block; font-size: 30px; color: var(--tinta); font-weight: normal; }
nav { display: flex; gap: 24px; margin-top: 24px; font-size: 14px; }
a { color: var(--azul); text-underline-offset: 4px; }
nav a { text-decoration: none; }
nav a:hover { text-decoration: underline; }
a:focus-visible { outline: 3px solid var(--azul); outline-offset: 4px; }
.indicadores { display: grid; grid-template-columns: repeat(4, 1fr); padding: 25px 0; margin: 0; border-bottom: 1px solid var(--linea); }
.indicador { padding: 0 22px; border-right: 1px solid var(--linea); }
.indicador:first-child { padding-left: 0; }
.indicador:last-child { border: 0; }
dt { color: var(--gris); font-size: 13px; }
dd { margin: 6px 0; font-size: 29px; font-variant-numeric: tabular-nums; }
.indicador p { font-size: 11px; margin: 0; color: var(--gris); }
section { padding: 32px 0; }
.seccion-titulo { display: flex; justify-content: space-between; align-items: baseline; gap: 16px; margin-bottom: 18px; }
h2 { margin: 0; font-size: 21px; font-weight: normal; }
.seccion-titulo p { margin: 0; font-size: 12px; color: var(--gris); }
.figuras { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start; }
figure { margin: 0; border: 1px solid var(--linea); background: white; }
figcaption { display: flex; gap: 14px; padding: 20px 20px 8px; }
.numero { color: var(--azul); font-size: 12px; padding-top: 4px; }
h3 { margin: 0; font-size: 17px; font-weight: normal; }
figcaption p { margin: 7px 0 0; color: var(--gris); font-size: 12px; }
figure a { display: block; padding: 8px; }
img { display: block; width: 100%; height: auto; }
.resultados { display: grid; grid-template-columns: 1fr 1fr; gap: 36px; border-top: 1px solid var(--linea); }
.resultados h2 { margin-bottom: 16px; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
caption { text-align: left; color: var(--gris); margin-bottom: 12px; font-size: 12px; }
th { text-align: left; font-weight: normal; color: var(--gris); font-size: 12px; }
th, td { padding: 11px 0; border-bottom: 1px solid var(--linea); }
th:last-child, td:last-child { text-align: right; font-variant-numeric: tabular-nums; }
.metodo p { color: var(--gris); font-size: 14px; margin: 0 0 14px; }
footer { border-top: 1px solid var(--linea); padding: 20px 0 30px; color: var(--gris); font-size: 12px; }
@media (max-width: 850px) { .figuras, .resultados { grid-template-columns: 1fr; } .indicadores { grid-template-columns: 1fr 1fr; gap: 24px 0; } .indicador:nth-child(3) { padding-left: 0; } .indicador:nth-child(2) { border: 0; } }
@media (max-width: 480px) { .contenedor { padding: 0 18px; } .encabezado { flex-direction: column; } .periodo { border: 0; padding: 0; } .seccion-titulo { display: block; } dd { font-size: 24px; } nav { gap: 18px; } }
@media print { body { background: white; } nav { display: none; } .contenedor { padding: 0; } figure, .resultados { break-inside: avoid; } .figuras { gap: 12px; } }
</style>
</head>
<body>
<header><div class="contenedor">
<div class="encabezado"><div><p class="etiqueta">Minería de datos · Informe de resultados</p><h1>Salud, desarrollo y emisiones</h1><p class="subtitulo">Una comparación de la esperanza de vida, el PIB y las emisiones de CO₂ por habitante entre países y territorios.</p></div><div class="periodo">Año de análisis<strong>__ANIO__</strong></div></div>
<nav aria-label="Secciones del informe"><a href="#figuras">Gráficos</a><a href="#resultados">Resultados</a><a href="#metodo">Metodología</a></nav>
</div></header>
<main class="contenedor">
<dl class="indicadores" aria-label="Indicadores del año">__TARJETAS__</dl>
<section id="figuras"><div class="seccion-titulo"><h2>Comparación visual</h2><p>Selecciona una figura para abrirla en tamaño completo.</p></div><div class="figuras">__GRAFICOS__</div></section>
<section class="resultados" id="resultados">
<div><h2>Mayor esperanza de vida</h2><table><caption>Cinco países y territorios de la muestra · __ANIO__</caption><thead><tr><th scope="col">País o territorio</th><th scope="col">Región</th><th scope="col">Esperanza de vida</th></tr></thead><tbody>__FILAS__</tbody></table></div>
<div class="metodo" id="metodo"><h2>Lectura de los resultados</h2><p>La correlación entre PIB por habitante y esperanza de vida es <strong>__CORRELACION__</strong>. Describe una asociación entre ambas variables en esta muestra; no demuestra una relación causal.</p><p>La muestra conserva las coincidencias de país, código y año entre las tres fuentes. Los indicadores resumen países y territorios sin ponderar por población.</p><p>En la limpieza, si los valores inválidos o nulos superan el 5 %, se completan con el promedio de la fuente; con 5 % o menos, se eliminan las filas afectadas.</p><p>La evolución histórica usa los datos de esperanza de vida desde 1990. Los demás gráficos corresponden a __ANIO__.</p></div>
</section>
</main>
<footer><div class="contenedor">Fuentes: archivos de Our World in Data y Banco Mundial utilizados en el proyecto. Las unidades de PIB y CO₂ se conservan según las fuentes originales.</div></footer>
</body>
</html>'''
    for marcador, contenido in {
        "__ANIO__": str(anio), "__TARJETAS__": tarjetas,
        "__GRAFICOS__": graficos, "__FILAS__": filas,
        "__CORRELACION__": numero(correlacion, 2),
    }.items():
        html = html.replace(marcador, contenido)
    archivo = carpeta / "index.html"
    archivo.write_text(html, encoding="utf-8")
    return archivo
