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


# --- Programa principal ---

def main():
    print("demanda:")
    guardar(limpiar_demanda(), "demanda")

    print("\nLimpieza terminada.")


if __name__ == "__main__":
    main()
