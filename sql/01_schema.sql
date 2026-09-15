DROP TABLE IF EXISTS fact_accidente;
DROP TABLE IF EXISTS dim_empresa;
DROP TABLE IF EXISTS dim_unidad;
DROP TABLE IF EXISTS dim_tipo;
DROP TABLE IF EXISTS dim_tiempo;

CREATE TABLE dim_empresa (
    id_empresa INTEGER PRIMARY KEY,
    titular VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE dim_unidad (
    id_unidad INTEGER PRIMARY KEY,
    unidad VARCHAR(200) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    provincia VARCHAR(100) NOT NULL,
    distrito VARCHAR(100) NOT NULL,
    UNIQUE (unidad, departamento, provincia, distrito)
);

CREATE TABLE dim_tipo (
    id_tipo INTEGER PRIMARY KEY,
    tipo_accidente VARCHAR(250) NOT NULL UNIQUE,
    familia VARCHAR(80) NOT NULL
);

CREATE TABLE dim_tiempo (
    fecha DATE PRIMARY KEY,
    anio SMALLINT NOT NULL,
    mes SMALLINT NOT NULL,
    trimestre SMALLINT NOT NULL,
    nombre_mes VARCHAR(12) NOT NULL,
    dato_confiable BOOLEAN NOT NULL
);

CREATE TABLE fact_accidente (
    id_accidente INTEGER PRIMARY KEY,
    id_evento INTEGER NOT NULL,
    id_empresa INTEGER NOT NULL REFERENCES dim_empresa (id_empresa),
    id_unidad INTEGER NOT NULL REFERENCES dim_unidad (id_unidad),
    id_tipo INTEGER NOT NULL REFERENCES dim_tipo (id_tipo),
    fecha_accidente DATE NOT NULL REFERENCES dim_tiempo (fecha),
    fecha_fallecimiento DATE,
    dias_hasta_fallecimiento SMALLINT,
    fecha_inconsistente BOOLEAN NOT NULL,
    victimas_evento SMALLINT NOT NULL,
    categoria VARCHAR(40) NOT NULL
);

CREATE INDEX idx_fact_fecha ON fact_accidente (fecha_accidente);
CREATE INDEX idx_fact_tipo ON fact_accidente (id_tipo);
CREATE INDEX idx_fact_unidad ON fact_accidente (id_unidad);

INSERT INTO dim_tiempo (fecha, anio, mes, trimestre, nombre_mes, dato_confiable)
SELECT
    d::date,
    EXTRACT(YEAR FROM d)::smallint,
    EXTRACT(MONTH FROM d)::smallint,
    EXTRACT(QUARTER FROM d)::smallint,
    (ARRAY['Enero','Febrero','Marzo','Abril','Mayo','Junio',
           'Julio','Agosto','Setiembre','Octubre','Noviembre','Diciembre'])
        [EXTRACT(MONTH FROM d)],
    EXTRACT(YEAR FROM d) NOT IN (2017, 2018, 2019)
FROM generate_series('2002-01-01'::date, '2021-12-31'::date, '1 day') AS d;