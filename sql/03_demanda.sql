-- =====================================================================
-- 03_demanda.sql
-- Pregunta 4: ¿Cómo evoluciona la demanda (estacionalidad, picos, tendencia)?
-- =====================================================================


-- Demanda eléctrica de cada año, en GWh: total y media diaria
-- (la media diaria permite comparar años con distinto número de días, como los bisiestos)
SELECT
    EXTRACT(YEAR FROM fecha)          AS anio,
    ROUND(SUM(demanda_mwh) / 1000, 1) AS demanda_gwh,
    ROUND(AVG(demanda_mwh) / 1000, 1) AS media_diaria_gwh
FROM demanda
GROUP BY anio
ORDER BY anio;


-- Estacionalidad: demanda media diaria de cada mes del año, en GWh (todos los años juntos)
-- (la media diaria evita que los meses con menos días, como febrero, parezcan más bajos)
SELECT
    EXTRACT(MONTH FROM fecha)         AS mes,
    ROUND(AVG(demanda_mwh) / 1000, 1) AS media_diaria_gwh
FROM demanda
GROUP BY mes
ORDER BY mes;


-- Picos: los 10 días con mayor demanda de todo el periodo, en GWh
-- (no se agrupa: cada fila de la tabla ya es un día)
SELECT
    fecha,
    ROUND(demanda_mwh / 1000, 1) AS demanda_gwh
FROM demanda
ORDER BY demanda_gwh DESC
LIMIT 10;
