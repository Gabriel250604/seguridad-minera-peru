# Seguridad Minera Perú

Análisis de los accidentes mortales registrados en la minería peruana entre 2002 y 2021, desde el dato crudo publicado por el MINEM hasta un tablero de Business Intelligence.

> **Estado del proyecto:** en construcción. Fase 0 de 5 completada.

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

_Pendiente: se documentarán al completar la fase de limpieza._

## Hallazgos

_Pendiente._

## Limitaciones conocidas

- El dataset no distingue entre trabajadores de empresas contratistas y de titulares mineros, por lo que no es posible analizar esa diferencia.
- No existe un denominador de exposición, como horas trabajadas o número de trabajadores, por lo que no se pueden construir tasas de accidentabilidad comparables entre empresas. Cualquier conteo absoluto favorece a las operaciones grandes.
- El periodo 2017 – 2019 presenta un subregistro evidente que se documenta en el análisis y se señala en el tablero.

## Autor

Gabriel Enrique Melchor Enciso
Estudiante de Ingeniería de Sistemas de Información, Universidad Peruana de Ciencias Aplicadas
