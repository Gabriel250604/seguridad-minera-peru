SELECT 'Total victimas' AS control, COUNT(*)::text AS valor FROM fact_accidente
UNION ALL
SELECT 'Eventos distintos', COUNT(DISTINCT id_evento)::text FROM fact_accidente
UNION ALL
SELECT 'Empresas', COUNT(*)::text FROM dim_empresa
UNION ALL
SELECT 'Unidades', COUNT(*)::text FROM dim_unidad
UNION ALL
SELECT 'Tipos de accidente', COUNT(*)::text FROM dim_tipo
UNION ALL
SELECT 'Familias', COUNT(DISTINCT familia)::text FROM dim_tipo
UNION ALL
SELECT 'Dias en dim_tiempo', COUNT(*)::text FROM dim_tiempo
UNION ALL
SELECT 'Fechas inconsistentes', COUNT(*)::text FROM fact_accidente WHERE fecha_inconsistente
UNION ALL
SELECT 'Huerfanos de empresa', COUNT(*)::text
FROM fact_accidente f LEFT JOIN dim_empresa d ON f.id_empresa = d.id_empresa
WHERE d.id_empresa IS NULL
UNION ALL
SELECT 'Huerfanos de unidad', COUNT(*)::text
FROM fact_accidente f LEFT JOIN dim_unidad d ON f.id_unidad = d.id_unidad
WHERE d.id_unidad IS NULL
UNION ALL
SELECT 'Huerfanos de tipo', COUNT(*)::text
FROM fact_accidente f LEFT JOIN dim_tipo d ON f.id_tipo = d.id_tipo
WHERE d.id_tipo IS NULL;

SELECT t.anio, COUNT(*) AS victimas, COUNT(DISTINCT f.id_evento) AS eventos
FROM fact_accidente f
JOIN dim_tiempo t ON f.fecha_accidente = t.fecha
GROUP BY t.anio
ORDER BY t.anio;

SELECT d.familia, COUNT(*) AS victimas
FROM fact_accidente f
JOIN dim_tipo d ON f.id_tipo = d.id_tipo
GROUP BY d.familia
ORDER BY victimas DESC;

SELECT
    ROUND(AVG(dias_hasta_fallecimiento), 2) AS promedio_dias,
    COUNT(dias_hasta_fallecimiento) AS casos_con_dato,
    COUNT(*) FILTER (WHERE dias_hasta_fallecimiento = 0) AS muertes_inmediatas
FROM fact_accidente;