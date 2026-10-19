# Proyecto: Análisis del mercado eléctrico español

## Contexto
Soy Cristobal, graduado en Matemáticas Aplicadas.
Este es un proyecto de portfolio para demostrar SQL, Python, Excel y visualización.
Trabajo en Mac. No uso máquinas virtuales ni Windows.

## Objetivo
Analizar el mercado eléctrico español con datos públicos de Red Eléctrica (API REData):
demanda, generación por tecnología, precios y emisiones.

Preguntas del análisis:
1. ¿Cómo ha cambiado el mix energético (peso de las renovables) año a año?
2. ¿Cuándo es más barata la electricidad (hora, día de la semana, estación)?
3. ¿Abarata la producción solar/eólica el precio?
4. ¿Cómo evoluciona la demanda (estacionalidad, picos, tendencia)?
5. ¿Qué días han sido anómalos (precios extremos, récords)?

## Herramientas
- Python (requests, pandas) en VS Code: extracción y limpieza
- PostgreSQL + DBeaver: almacenamiento y análisis SQL
- Excel para Mac (Power Query, tablas dinámicas): análisis complementario
- Power BI Service (versión web, en el navegador): dashboard final.
  Power BI Desktop NO está disponible en Mac y no uso máquina virtual.
  Fuente de datos para Power BI: tablas finales exportadas de PostgreSQL a Excel, guardado en OneDrive.
- Git + GitHub: control de versiones y publicación (el dashboard se mostrará con capturas y vídeo en el README)

## Fases
1. Preparación del entorno y repositorio
2. Extracción de datos de la API en Python
3. Limpieza y transformación en Python
4. Diseño de la base de datos y carga en PostgreSQL
5. Análisis en SQL (lo hago yo; Claude revisa)
6. Análisis complementario en Excel
7. Dashboard en Power BI web (Power Query online, modelo semántico y medidas DAX)
8. README final con conclusiones

## Cómo quiero que trabajes conmigo (MUY IMPORTANTE)
Mi objetivo es APRENDER y poder defender cada parte del proyecto en una entrevista.

- Ve paso a paso. Haz una sola cosa cada vez y espera a que te confirme antes de seguir.
- Antes de escribir código, explícame qué vas a hacer y por qué.
- Después de escribir código, explícamelo bloque a bloque en lenguaje sencillo.
- Pregúntame antes de tomar decisiones de diseño (estructura de tablas, cómo tratar nulos, etc.).
- Las consultas SQL del análisis (fase 5) las escribo YO. No me des la solución:
  dame pistas, revisa lo que escribo y explícame alternativas o mejoras.
- La interpretación de los datos y las conclusiones son mías. Puedes hacerme preguntas que me ayuden a pensar.
- Si algo falla, explícame la causa del error, no solo el arreglo.
- Responde siempre en español.
- Código claro y comentado en español, sin sobreingeniería.
- Haz commits pequeños y con mensajes descriptivos en español, y avísame antes de hacerlos.
- Nunca subas a GitHub datos sensibles, claves ni archivos de datos pesados.
