-- =====================================================================
-- 03_demanda.sql
-- Pregunta 4: ¿Cómo evoluciona la demanda (estacionalidad, picos, tendencia)?
-- =====================================================================


-- Demanda eléctrica total de cada año, en GWh
SELECT
    EXTRACT(YEAR FROM fecha)          AS anio,
    ROUND(SUM(demanda_mwh) / 1000, 1) AS demanda_gwh
FROM demanda
GROUP BY anio
ORDER BY anio;
