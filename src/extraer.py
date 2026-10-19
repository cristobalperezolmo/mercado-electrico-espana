"""
Extracción de datos de la API REData de Red Eléctrica.

Descarga demanda, generación, emisiones (por día) y precios (por hora)
del periodo configurado y guarda un CSV por tema en data/raw/.
Los datos se guardan tal cual llegan de la API: solo se aplana el JSON, sin limpiar nada.

Uso (desde la carpeta del proyecto):
    python src/extraer.py
"""

import time
from pathlib import Path

import pandas as pd
import requests


# --- 1. Configuración ---

URL_BASE = "https://apidatos.ree.es/es/datos"

FECHA_INICIO = "2019-01-01"
FECHA_FIN = "2025-12-31"

# Para cada tema: endpoint, agrupación temporal y tamaño máximo de cada tramo.
# "YS" = tramos de un año, "MS" = tramos de un mes (límites de la API).
TEMAS = {
    "demanda": {
        "endpoint": "demanda/evolucion",
        "time_trunc": "day",
        "tramo": "YS",
    },
    "generacion": {
        "endpoint": "generacion/estructura-generacion",
        "time_trunc": "day",
        "tramo": "YS",
    },
    "emisiones": {
        "endpoint": "generacion/no-renovables-detalle-emisiones-CO2",
        "time_trunc": "day",
        "tramo": "YS",
    },
    "precios": {
        "endpoint": "mercados/precios-mercados-tiempo-real",
        "time_trunc": "hour",
        "tramo": "MS",
    },
}

REINTENTOS = 3            # intentos máximos si el servidor falla (errores 5xx)
ESPERA_REINTENTO = 10     # segundos de espera antes de reintentar
PAUSA_ENTRE_PETICIONES = 1  # segundos entre peticiones, para no saturar la API

# Carpeta de salida: data/raw dentro del proyecto, se ejecute desde donde se ejecute
CARPETA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"


# --- 2. Trocear el periodo en tramos que la API acepte ---

def generar_tramos(inicio, fin, tamano):
    """Devuelve una lista de pares (fecha_inicio, fecha_fin) que cubren todo el periodo."""
    inicios = pd.date_range(start=inicio, end=fin, freq=tamano)
    tramos = []

    for i, inicio_tramo in enumerate(inicios):
        # El tramo acaba el día antes de que empiece el siguiente (o en la fecha final)
        if i + 1 < len(inicios):
            fin_tramo = inicios[i + 1] - pd.Timedelta(days=1)
        else:
            fin_tramo = pd.Timestamp(fin)
        tramos.append((inicio_tramo.strftime("%Y-%m-%d"), fin_tramo.strftime("%Y-%m-%d")))

    return tramos


# --- 3. Hacer una petición con reintentos ---

def pedir(url, parametros):
    """Pide datos a la API. Reintenta si el servidor falla; se detiene si la petición es incorrecta."""
    for intento in range(1, REINTENTOS + 1):
        try:
            respuesta = requests.get(url, params=parametros, timeout=60)
        except requests.exceptions.RequestException as error:
            # Sin conexión, tiempo de espera agotado...: se trata como un fallo temporal
            print(f"    Error de conexión ({error}). Intento {intento}/{REINTENTOS}")
        else:
            if respuesta.status_code == 200:
                return respuesta.json()

            if respuesta.status_code >= 500:
                # Error del servidor (p. ej. 503): es temporal, merece la pena reintentar
                print(f"    Error {respuesta.status_code} del servidor. Intento {intento}/{REINTENTOS}")
            else:
                # Error de la petición (p. ej. 400): reintentar no sirve de nada
                raise RuntimeError(
                    f"La API rechazó la petición ({respuesta.status_code}): {respuesta.text[:200]}\n"
                    f"Parámetros: {parametros}"
                )

        if intento < REINTENTOS:
            time.sleep(ESPERA_REINTENTO)

    raise RuntimeError(f"La API no respondió tras {REINTENTOS} intentos. Parámetros: {parametros}")


# --- 4. Convertir la respuesta JSON en una tabla ---

def json_a_tabla(datos):
    """Aplana el JSON de la API: una fila por valor, con el nombre y el tipo de su serie."""
    tablas = []

    for serie in datos["included"]:
        tabla = pd.DataFrame(serie["attributes"]["values"])
        tabla["serie"] = serie["attributes"]["title"]
        tabla["tipo"] = serie["attributes"]["type"]
        tablas.append(tabla)

    return pd.concat(tablas, ignore_index=True)


# --- 5. Programa principal ---

def main():
    CARPETA_RAW.mkdir(parents=True, exist_ok=True)

    for tema, config in TEMAS.items():
        url = f"{URL_BASE}/{config['endpoint']}"
        tramos = generar_tramos(FECHA_INICIO, FECHA_FIN, config["tramo"])
        print(f"\n{tema}: {len(tramos)} tramos")

        tablas = []
        for numero, (inicio, fin) in enumerate(tramos, start=1):
            print(f"  Tramo {numero}/{len(tramos)}: {inicio} a {fin}")
            parametros = {
                "start_date": f"{inicio}T00:00",
                "end_date": f"{fin}T23:59",
                "time_trunc": config["time_trunc"],
            }
            datos = pedir(url, parametros)
            tablas.append(json_a_tabla(datos))
            time.sleep(PAUSA_ENTRE_PETICIONES)

        df = pd.concat(tablas, ignore_index=True)
        ruta = CARPETA_RAW / f"{tema}.csv"
        df.to_csv(ruta, index=False)
        print(f"  Guardado {ruta.name}: {len(df):,} filas")

    print("\nExtracción terminada.")


# Solo se ejecuta main() si lanzamos este archivo directamente
if __name__ == "__main__":
    main()
