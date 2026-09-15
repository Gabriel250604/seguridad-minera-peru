# Seguridad Minera Perú

Análisis de los accidentes mortales registrados en la minería peruana entre 2002 y 2021, desde el dato crudo publicado por el MINEM hasta un tablero de Business Intelligence.

> **Estado del proyecto:** Fases 0 a 2 completadas. Pendiente el modelado en PostgreSQL y el tablero.

## Contexto

El Ministerio de Energía y Minas publica el registro de accidentes mortales ocurridos en unidades mineras del país. Este proyecto toma ese archivo, lo procesa y lo lleva a un modelo analítico para responder tres preguntas:

- ¿Cómo ha evolucionado la cantidad de accidentes mortales a lo largo de veinte años?
- ¿Qué tipos de accidente concentran la mayor cantidad de víctimas?
- ¿Cómo se distribuyen geográficamente y en qué medida se concentran en pocas unidades mineras?

## Fuente de datos

| Campo | Detalle |
|---|---|
| Dataset | Accidentes Mortales en Mina |
| Entidad | Ministerio de Energía y Minas (MINEM) |
| Portal | Plataforma Nacional de Datos Abiertos del Perú |
| Formato original | CSV, separador `;`, codificación ISO-8859-1 |
| Volumen | 901 registros, 9 columnas |
| Interpretación | 901 víctimas distribuidas en 784 eventos |
| Periodo | 2002 – 2021 |
| Fecha de descarga | 13/09/2026 |
| Condiciones de uso | Datos abiertos de libre uso, citando la fuente |

## Arquitectura

    CSV (MINEM)  ->  Python / pandas  ->  PostgreSQL  ->  Power BI
     extracción      limpieza y ETL     modelo estrella   tablero

| Etapa | Herramienta | Salida |
|---|---|---|
| Extracción | pandas | DataFrame crudo |
| Limpieza y transformación | pandas | `data/processed/accidentes_limpio.csv` |
| Modelado | PostgreSQL | Modelo estrella: 4 dimensiones y 1 tabla de hechos |
| Visualización | Power BI | Tablero de 4 páginas |

## Estructura del repositorio

    data/raw/         Archivo original del MINEM, sin modificar
    data/processed/   Salidas del pipeline (no versionadas)
    notebooks/        Exploración de datos
    src/              Scripts del pipeline
    sql/              Esquema y consultas de validación
    powerbi/          Archivo .pbix
    docs/             Capturas y notas

## Cómo reproducirlo

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

Luego copiar `.env.example` como `.env` y completar las credenciales de la base de datos local.

## Decisiones de tratamiento del dato

### Duplicados exactos: se conservan

El dataset contiene 101 filas idénticas en sus nueve columnas. Se decidió conservarlas, tratando cada fila como una víctima, por dos razones.

La primera es la distribución de los tipos de accidente. Entre las filas duplicadas están sobre-representados justamente los siniestros de víctimas múltiples, con frecuencias de dos a cuatro veces superiores a las del conjunto completo:

| Tipo de accidente | En duplicados | En el total |
|---|---:|---:|
| Ahogamiento por inundación | 4.1% | 1.0% |
| Atrapada entre dos objetos móviles | 4.7% | 1.6% |
| Golpes por detonación de explosivos | 7.1% | 2.9% |
| Atrapado por derrumbe o deslizamiento | 15.3% | 7.4% |
| Intoxicación, asfixia, absorción | 11.2% | 5.8% |
| Desprendimiento de rocas | 22.9% | 26.6% |

El desprendimiento de rocas, que por su naturaleza suele cobrar una sola vida, es el único sub-representado. Si los duplicados fueran errores de carga, su distribución sería equivalente a la del conjunto.

La segunda razón es que existen eventos con varias filas y distinta fecha de fallecimiento, lo que indica que el registro es por persona y no por evento.

En consecuencia se incorpora el campo `ID_EVENTO`, construido a partir de la combinación de titular, unidad, ubicación, tipo de accidente, categoría y fecha del accidente. Esto permite reportar ambas magnitudes por separado: víctimas y eventos.

La alternativa descartada, eliminar los duplicados, queda documentada como línea comentada en el script de limpieza.

### Valores nulos

`CATEGORIA` presenta 68 nulos, equivalentes al 7.5% del total. Se asignan a la etiqueta "Sin categoría" en lugar de descartar los registros, ya que el resto de su información es válida. Las columnas de ubicación presentan 2 nulos correspondientes a los mismos dos registros.

### Agrupación de tipos de accidente

Los 39 valores originales de `TIPO_ACCIDENTE` se agrupan en 11 familias según el agente que produce la lesión. El mapeo vive en `src/mapeo_familias.py`, separado del script de limpieza, para que pueda auditarse sin leer el pipeline.

| Familia | Víctimas |
|---|---:|
| Desprendimiento de rocas y mineral | 337 |
| Tránsito y transporte | 124 |
| Caída de personas | 92 |
| Maquinaria y atrapamiento | 90 |
| Objetos y materiales | 76 |
| Atmósfera y sustancias peligrosas | 75 |
| Energía eléctrica | 35 |
| Otros | 27 |
| Explosivos | 26 |
| Fenómenos naturales | 14 |
| Esfuerzos físicos | 5 |

Tres casos requirieron criterio:

- `EXPOSICIÓN A, O CONTACTO CON RADIACIONES` se unifica con `INTOXICACION-ASFIXIA-ABSORCION-RADIACIONES`, ya que el segundo tipo comprende explícitamente las radiaciones y el dataset no ofrece ningún elemento que permita distinguirlos.
- `OTROS TIPOS - DESCARGA ELECTRICA POR RAYO` se clasifica como fenómeno natural y no como energía eléctrica, porque su control corresponde a protocolos de tormenta y no a procedimientos sobre instalaciones eléctricas.
- `OTROS TIPOS - CAUSA NATURAL` se asigna a Otros, dado que en registros de seguridad minera designa fallecimientos por causa médica y no eventos de la naturaleza.

La fuente presenta además dos inconsistencias de escritura: `EXPOSICIÓN A, O CONTACTO CON, LA CORRIENTE ELÉCTRICA`, con un único caso, es el mismo tipo que `EXPOSICIÓN A, O CONTACTO CON ENERGÍA ELÉCTRICA`, y `OTRO TIPOS - CAMPANEO` omite la letra ese del prefijo. Ambos se mapean a la familia que les corresponde.

### Fechas de fallecimiento anteriores al accidente

19 registros, el 2.1% del total, presentan una fecha de fallecimiento anterior a la del accidente. Se conserva la fila, porque corresponde a una víctima real, se deja nulo el campo `DIAS_HASTA_FALLECIMIENTO` y se marca con la bandera `FECHA_INCONSISTENTE`. El promedio de días hasta el fallecimiento se calcula en consecuencia sobre 882 casos.

## Hallazgos preliminares

- **Subregistro entre 2017 y 2019.** La serie se mantiene entre 47 y 69 registros anuales desde 2002 hasta 2016, cae a 6 en 2017 y 4 en 2018, no presenta ningún registro en 2019, y vuelve a 73 en 2020. La magnitud del salto descarta una mejora real en la seguridad y apunta a un vacío de reporte.
- **Concentración por familia de accidente.** Tras agrupar los 39 tipos originales en 11 familias, el desprendimiento de rocas y mineral concentra 337 de las 901 víctimas, el 37% del total y casi tres veces más que la segunda familia. Considerado como tipo individual, el desprendimiento de rocas explica por sí solo 240 víctimas.
- **Los siniestros de víctimas múltiples son minoría pero pesan.** Las 901 víctimas se distribuyen en 784 eventos: 74 eventos concentraron más de una víctima y explican 191 fallecimientos, el 21% del total.
- **Inconsistencias en las fechas.** 19 registros presentan fecha de fallecimiento anterior a la del accidente, concentrados en 2020.

## Limitaciones conocidas

- El dataset no distingue entre trabajadores de empresas contratistas y de titulares mineros, por lo que no es posible analizar esa diferencia.
- No existe un denominador de exposición, como horas trabajadas o número de trabajadores, por lo que no se pueden construir tasas de accidentabilidad comparables entre empresas. Cualquier conteo absoluto favorece a las operaciones grandes.
- El periodo 2017 – 2019 presenta un subregistro evidente que se documenta en el análisis y se señala en el tablero.
- Algunos registros de 2020 presentan fechas de fallecimiento anteriores a la del accidente, lo que afecta el cálculo de días transcurridos hasta el deceso en esos casos.
- El dataset no incluye identificador de persona, por lo que la distinción entre víctimas y eventos se infiere a partir de la combinación de campos descrita en la sección de decisiones.

## Autor

Gabriel Enrique Melchor Enciso
Estudiante de Ingeniería de Sistemas de Información, Universidad Peruana de Ciencias Aplicadas