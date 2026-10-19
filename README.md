# Análisis del mercado eléctrico español

Proyecto de análisis de datos sobre el mercado eléctrico en España a partir de los datos
públicos de Red Eléctrica (API REData): demanda, generación por tecnología, precios y emisiones.

> 🚧 **Estado:** en desarrollo.

## Preguntas del análisis

1. ¿Cómo ha cambiado el mix energético (peso de las renovables) año a año?
2. ¿Cuándo es más barata la electricidad (hora, día de la semana, estación)?
3. ¿Abarata la producción solar/eólica el precio?
4. ¿Cómo evoluciona la demanda (estacionalidad, picos, tendencia)?
5. ¿Qué días han sido anómalos (precios extremos, récords)?

## Herramientas

- **Python** (requests, pandas): extracción y limpieza de datos
- **PostgreSQL**: almacenamiento y análisis en SQL
- **Excel**: análisis complementario (Power Query, tablas dinámicas)
- **Power BI**: dashboard final
- **Git y GitHub**: control de versiones

## Estructura del proyecto

```
data/raw/         datos originales de la API (no incluidos en el repositorio)
data/processed/   datos limpios (no incluidos en el repositorio)
notebooks/        exploración de datos
src/              scripts de extracción, limpieza y carga
sql/              creación de tablas y consultas de análisis
excel/            análisis complementario
powerbi/          capturas del dashboard
```

## Cómo reproducir el entorno

Requisitos: Python 3.11 o superior y PostgreSQL.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
