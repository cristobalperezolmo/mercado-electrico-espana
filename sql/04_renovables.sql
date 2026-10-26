-- =====================================================================
-- 04_renovables.sql
-- Pregunta 1: ¿Cómo ha cambiado el mix energético (peso de las renovables) año a año?
-- =====================================================================


-- Generación renovable, generación total y porcentaje renovable de cada año
-- (se une generacion con tecnologias para saber qué tecnologías son renovables;
--  el porcentaje se calcula con los totales del año, no como media de porcentajes diarios)
SELECT
    EXTRACT(YEAR FROM g.fecha)                                                 AS anio,
    ROUND(SUM(g.generacion_mwh) FILTER (WHERE t.es_renovable) / 1000, 1)       AS renovable_gwh,
    ROUND(SUM(g.generacion_mwh) / 1000, 1)                                     AS total_gwh,
    ROUND(SUM(g.generacion_mwh) FILTER (WHERE t.es_renovable)
          / SUM(g.generacion_mwh) * 100, 1)                                    AS porcentaje_renovable
FROM generacion g
JOIN tecnologias t ON t.tecnologia = g.tecnologia
GROUP BY anio
ORDER BY anio;
