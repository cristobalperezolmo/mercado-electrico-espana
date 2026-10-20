"""
Limpieza de los datos en bruto de la API REData.

Lee los CSV de data/raw/, los limpia, comprueba que el resultado es correcto
y lo guarda en data/processed/. Los archivos de data/raw/ nunca se modifican.

Uso (desde la carpeta del proyecto):
    python src/limpiar.py
"""

from pathlib import Path

import pandas as pd


# --- Configuración ---

CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_RAW = CARPETA_PROYECTO / "data" / "raw"
CARPETA_PROCESSED = CARPETA_PROYECTO / "data" / "processed"

# Periodo descargado: se usa para comprobar que no falta ningún día
FECHA_INICIO = "2019-01-01"
FECHA_FIN = "2025-12-31"


# --- Funciones auxiliares ---

def comprobar(condicion, mensaje):
    """Detiene el script con un mensaje claro si la condición no se cumple."""
    if not condicion:
        raise ValueError(f"Comprobación fallida: {mensaje}")


def guardar(df, nombre):
    """Guarda la tabla limpia en data/processed/ como CSV."""
    CARPETA_PROCESSED.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_PROCESSED / f"{nombre}.csv"
    df.to_csv(ruta, index=False)
    print(f"  Guardado {ruta.name}: {len(df):,} filas, columnas {list(df.columns)}")


# --- Limpieza por tema ---

def limpiar_demanda():
    """Demanda diaria: una fila por día con la fecha y la demanda en MWh."""
    df = pd.read_csv(CARPETA_RAW / "demanda.csv")

    # Antes de descartar columnas, comprobamos que de verdad no aportan información
    comprobar((df["serie"] == "Demanda").all(), "la columna 'serie' tiene valores distintos de 'Demanda'")
    comprobar((df["percentage"] == 1).all(), "la columna 'percentage' tiene valores distintos de 1")
    comprobar(df["tipo"].isna().all(), "la columna 'tipo' no está vacía")

    # Fecha: los 10 primeros caracteres del texto ('2019-01-01') convertidos en fecha
    df["fecha"] = pd.to_datetime(df["datetime"].str[:10], format="%Y-%m-%d")

    # Nombre que dice qué es y en qué unidad está
    df = df.rename(columns={"value": "demanda_mwh"})

    # Nos quedamos solo con las columnas útiles, ordenadas por fecha
    df = df[["fecha", "demanda_mwh"]].sort_values("fecha").reset_index(drop=True)

    # Comprobaciones del resultado
    dias_esperados = pd.date_range(FECHA_INICIO, FECHA_FIN, freq="D")
    comprobar(not df["fecha"].duplicated().any(), "hay fechas repetidas")
    comprobar(set(df["fecha"]) == set(dias_esperados), "faltan o sobran días en el periodo")
    comprobar(df["demanda_mwh"].notna().all(), "hay demandas vacías")
    comprobar((df["demanda_mwh"] > 0).all(), "hay demandas menores o iguales a 0")

    return df


def limpiar_generacion():
    """Generación diaria por tecnología: una fila por día y tecnología, en MWh."""
    df = pd.read_csv(CARPETA_RAW / "generacion.csv")
    df["fecha"] = pd.to_datetime(df["datetime"].str[:10], format="%Y-%m-%d")

    # "Fuel + Gas" solo tiene valores de ±0,001 MWh (ruido de redondeo): se elimina.
    # Antes comprobamos que sigue siendo ruido, por si algún día trae valores reales.
    fuel_gas = df["serie"] == "Fuel + Gas"
    comprobar((df.loc[fuel_gas, "value"].abs() < 1).all(), "'Fuel + Gas' tiene valores de 1 MWh o más")
    df = df[~fuel_gas]

    # Separamos el total de la API de las tecnologías
    es_total = df["serie"] == "Generación total"
    total_api = df[es_total].set_index("fecha")["value"]
    df = df[~es_total]

    # Control: la suma de las tecnologías de cada día debe coincidir con el total de la API
    # (tolerancia de 1 MWh por los redondeos)
    suma_tecnologias = df.groupby("fecha")["value"].sum()
    diferencia = (suma_tecnologias - total_api).abs()
    comprobar((diferencia < 1).all(), "la suma de las tecnologías no coincide con el total de la API")

    # Nombres que dicen qué es cada columna y en qué unidad está
    df = df.rename(columns={"serie": "tecnologia", "value": "generacion_mwh"})

    # Columnas útiles, ordenadas por fecha y tecnología
    df = df[["fecha", "tecnologia", "tipo", "generacion_mwh"]]
    df = df.sort_values(["fecha", "tecnologia"]).reset_index(drop=True)

    # Comprobaciones del resultado
    dias_esperados = pd.date_range(FECHA_INICIO, FECHA_FIN, freq="D")
    comprobar(not df.duplicated(["fecha", "tecnologia"]).any(), "hay combinaciones fecha-tecnología repetidas")
    comprobar(set(df["tipo"]) == {"Renovable", "No-Renovable"}, f"tipos inesperados: {set(df['tipo'])}")
    comprobar(set(df["fecha"]) == set(dias_esperados), "faltan o sobran días en el periodo")
    comprobar(df["generacion_mwh"].notna().all(), "hay generaciones vacías")

    return df


def limpiar_emisiones():
    """Emisiones diarias totales de CO2 equivalente: una fila por día, en toneladas.

    Solo se usa la serie del total de la API. El desglose por tecnología y la intensidad
    (tCO2 eq./MWh) de la API son incoherentes en 2020-2021, así que no se guardan.
    La intensidad se calculará después como emisiones / generación.
    """
    df = pd.read_csv(CARPETA_RAW / "emisiones.csv")

    # Nos quedamos solo con la serie del total
    df = df[df["serie"] == "Total tCO2 eq."].copy()
    comprobar(len(df) > 0, "no se encuentra la serie 'Total tCO2 eq.'")

    df["fecha"] = pd.to_datetime(df["datetime"].str[:10], format="%Y-%m-%d")
    df = df.rename(columns={"value": "emisiones_tco2"})

    df = df[["fecha", "emisiones_tco2"]].sort_values("fecha").reset_index(drop=True)

    # Comprobaciones del resultado
    dias_esperados = pd.date_range(FECHA_INICIO, FECHA_FIN, freq="D")
    comprobar(not df["fecha"].duplicated().any(), "hay fechas repetidas")
    comprobar(set(df["fecha"]) == set(dias_esperados), "faltan o sobran días en el periodo")
    comprobar(df["emisiones_tco2"].notna().all(), "hay emisiones vacías")
    comprobar((df["emisiones_tco2"] > 0).all(), "hay emisiones menores o iguales a 0")

    return df


def limpiar_precios():
    """Precio spot por hora: una fila por hora, con el instante, la fecha y la hora en hora española.

    Desde 2025 la API da el spot cada 15 minutos: se agrega a horas con la media.
    El PVPC se descarta (solo existe desde junio de 2021).
    """
    df = pd.read_csv(CARPETA_RAW / "precios.csv")

    # Solo esperamos dos series; si aparece otra, queremos enterarnos
    series = set(df["serie"])
    comprobar(series == {"Precio mercado spot", "PVPC"}, f"series inesperadas: {series}")
    df = df[df["serie"] == "Precio mercado spot"].copy()

    # Texto -> instante exacto. utc=True unifica los desfases +01:00 y +02:00
    df["instante"] = pd.to_datetime(df["datetime"], format="ISO8601", utc=True)

    # Inicio de la hora a la que pertenece cada valor. Se redondea en UTC porque
    # en hora local el "02:00" del cambio de hora de octubre es ambiguo.
    df["hora_utc"] = df["instante"].dt.floor("h")

    # Una fila por hora: media de los valores de esa hora y cuántos había
    df = df.groupby("hora_utc")["value"].agg(precio_eur_mwh="mean", valores="count").reset_index()

    # Cada hora debe formarse con 1 valor (hasta 2024) o con 4 cuartos de hora (2025)
    comprobar(df["valores"].isin([1, 4]).all(), "hay horas con un número incompleto de cuartos de hora")

    # Columnas en hora española: el instante con su desfase, la fecha y la hora (0-23)
    df["fecha_hora"] = df["hora_utc"].dt.tz_convert("Europe/Madrid")
    df["fecha"] = df["fecha_hora"].dt.tz_localize(None).dt.normalize()
    df["hora"] = df["fecha_hora"].dt.hour

    df = df[["fecha_hora", "fecha", "hora", "precio_eur_mwh"]].sort_values("fecha_hora").reset_index(drop=True)

    # Comprobaciones del resultado: están todas las horas del periodo, ni una más ni una menos
    horas_esperadas = pd.date_range(
        FECHA_INICIO,
        pd.Timestamp(FECHA_FIN) + pd.Timedelta(days=1),
        freq="h",
        tz="Europe/Madrid",
        inclusive="left",   # excluye la medianoche del día siguiente al final
    )
    comprobar(not df["fecha_hora"].duplicated().any(), "hay horas repetidas")
    comprobar(set(df["fecha_hora"]) == set(horas_esperadas), "faltan o sobran horas en el periodo")
    comprobar(df["precio_eur_mwh"].notna().all(), "hay precios vacíos")

    return df


# --- Programa principal ---

def main():
    print("demanda:")
    guardar(limpiar_demanda(), "demanda")

    print("generacion:")
    guardar(limpiar_generacion(), "generacion")

    print("emisiones:")
    guardar(limpiar_emisiones(), "emisiones")

    print("precios:")
    guardar(limpiar_precios(), "precios")

    print("\nLimpieza terminada.")


if __name__ == "__main__":
    main()
