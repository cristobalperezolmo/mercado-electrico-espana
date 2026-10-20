-- =====================================================================
-- 01_crear_tablas.sql
-- Crea las tablas de la base de datos mercado_electrico.
--
-- Uso (desde la carpeta del proyecto):
--     psql -d mercado_electrico -f sql/01_crear_tablas.sql
--
-- Se puede ejecutar varias veces: borra las tablas si ya existen y las
-- vuelve a crear vacías. Después hay que cargar los datos con 02_cargar_datos.sql.
-- =====================================================================


-- Borrar las tablas si existen (generacion primero, porque depende de tecnologias)
DROP TABLE IF EXISTS generacion;
DROP TABLE IF EXISTS tecnologias;
DROP TABLE IF EXISTS demanda;
DROP TABLE IF EXISTS emisiones;
DROP TABLE IF EXISTS precios;


-- Demanda eléctrica diaria de España
CREATE TABLE demanda (
    fecha        DATE           PRIMARY KEY,
    demanda_mwh  NUMERIC(12,3)  NOT NULL CHECK (demanda_mwh > 0)
);


-- Emisiones diarias totales de CO2 equivalente de la generación eléctrica
CREATE TABLE emisiones (
    fecha           DATE           PRIMARY KEY,
    emisiones_tco2  NUMERIC(12,3)  NOT NULL CHECK (emisiones_tco2 > 0)
);


-- Precio horario del mercado spot (sin restricción de signo: hay precios negativos reales)
CREATE TABLE precios (
    fecha_hora      TIMESTAMPTZ    PRIMARY KEY,   -- instante exacto con zona horaria
    fecha           DATE           NOT NULL,      -- fecha en hora española
    hora            SMALLINT       NOT NULL CHECK (hora BETWEEN 0 AND 23),  -- hora española
    precio_eur_mwh  NUMERIC(10,4)  NOT NULL
);


-- Tecnologías de generación y si son renovables (una fila por tecnología)
CREATE TABLE tecnologias (
    tecnologia    TEXT     PRIMARY KEY,
    es_renovable  BOOLEAN  NOT NULL
);


-- Generación eléctrica diaria por tecnología (sin restricción de signo:
-- es generación neta y puede ser negativa si la central consume más de lo que produce)
CREATE TABLE generacion (
    fecha           DATE           NOT NULL,
    tecnologia      TEXT           NOT NULL REFERENCES tecnologias (tecnologia),
    generacion_mwh  NUMERIC(12,3)  NOT NULL,
    PRIMARY KEY (fecha, tecnologia)
);
