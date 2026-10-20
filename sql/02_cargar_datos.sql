-- =====================================================================
-- 02_cargar_datos.sql
-- Carga los CSV limpios de data/processed/ en las tablas de mercado_electrico.
--
-- Uso (desde la carpeta del proyecto, porque las rutas de los CSV son relativas):
--     psql -d mercado_electrico -v ON_ERROR_STOP=1 -f sql/02_cargar_datos.sql
--
-- Se puede ejecutar varias veces: vacía las tablas antes de cargar.
-- Todo va dentro de una transacción: si algo falla, no se carga nada.
-- =====================================================================


BEGIN;

-- Vaciar todas las tablas (a la vez, porque generacion depende de tecnologias)
TRUNCATE generacion, tecnologias, demanda, emisiones, precios;


-- --- Tablas que se cargan directamente desde su CSV ---

\copy demanda   FROM 'data/processed/demanda.csv'   WITH (FORMAT csv, HEADER true)
\copy emisiones FROM 'data/processed/emisiones.csv' WITH (FORMAT csv, HEADER true)
\copy precios   FROM 'data/processed/precios.csv'   WITH (FORMAT csv, HEADER true)


-- --- Generación: el CSV tiene la columna 'tipo', que va a la tabla tecnologias ---

-- 1. Tabla temporal con la misma forma que el CSV (se borra sola al terminar la transacción)
CREATE TEMPORARY TABLE generacion_csv (
    fecha           DATE,
    tecnologia      TEXT,
    tipo            TEXT,
    generacion_mwh  NUMERIC(12,3)
) ON COMMIT DROP;

\copy generacion_csv FROM 'data/processed/generacion.csv' WITH (FORMAT csv, HEADER true)

-- 2. Una fila por tecnología. Si apareciera un tipo desconocido, el CASE daría NULL
--    y la restricción NOT NULL de es_renovable detendría la carga.
INSERT INTO tecnologias (tecnologia, es_renovable)
SELECT DISTINCT
    tecnologia,
    CASE tipo
        WHEN 'Renovable'    THEN TRUE
        WHEN 'No-Renovable' THEN FALSE
    END
FROM generacion_csv;

-- 3. La generación, sin la columna 'tipo'
INSERT INTO generacion (fecha, tecnologia, generacion_mwh)
SELECT fecha, tecnologia, generacion_mwh
FROM generacion_csv;

COMMIT;


-- --- Comprobación: filas cargadas en cada tabla ---

SELECT 'demanda'     AS tabla, COUNT(*) AS filas FROM demanda
UNION ALL
SELECT 'emisiones',             COUNT(*)          FROM emisiones
UNION ALL
SELECT 'precios',               COUNT(*)          FROM precios
UNION ALL
SELECT 'tecnologias',           COUNT(*)          FROM tecnologias
UNION ALL
SELECT 'generacion',            COUNT(*)          FROM generacion;
