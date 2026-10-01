"""Carga de archivos CSV y JOINs entre tablas."""

from pathlib import Path

import pandas as pd

# Carpeta data/ en la raíz del proyecto, sin depender del directorio de trabajo.
RUTA_DATOS = Path(__file__).resolve().parent.parent / "data"


def load_data(ruta=RUTA_DATOS):
    """
    Carga los 5 archivos CSV en DataFrames y convierte columnas de fecha a datetime.

    Recibe: ruta del directorio donde están los CSVs.
    Devuelve: diccionario con DataFrames individuales.
    """
    ruta = Path(ruta)
    df_empleados = pd.read_csv(ruta / "empleados.csv")
    df_locaciones = pd.read_csv(ruta / "locaciones.csv")
    df_turnos = pd.read_csv(ruta / "turnos.csv", parse_dates=["hora_inicio", "hora_fin"])
    df_rondas = pd.read_csv(ruta / "rondas.csv", parse_dates=["hora_inicio", "hora_final"])
    df_incidentes = pd.read_csv(ruta / "incidentes.csv", parse_dates=["fecha_hora"])

    dataframes = {
        "empleados": df_empleados,
        "locaciones": df_locaciones,
        "turnos": df_turnos,
        "rondas": df_rondas,
        "incidentes": df_incidentes,
    }

    print("Archivos CSV cargados:")
    for nombre, df in dataframes.items():
        print(f"  - {nombre}: {len(df)} registros, {len(df.columns)} columnas")

    return dataframes


def join_data(dataframes):
    """
    Realiza los JOINs necesarios entre las tablas para construir DataFrames consolidados.

    Recibe: diccionario con DataFrames individuales.
    Devuelve: DataFrames consolidados de turnos, rondas e incidentes.
    """
    df_empleados = dataframes["empleados"]
    df_locaciones = dataframes["locaciones"]
    df_turnos = dataframes["turnos"]
    df_rondas = dataframes["rondas"]
    df_incidentes = dataframes["incidentes"]

    # JOIN: turnos con empleados y locaciones
    df_turnos_completo = df_turnos.merge(
        df_empleados, left_on="empleado_id", right_on="id", suffixes=("", "_empleado")
    ).merge(
        df_locaciones, left_on="locacion_id", right_on="id", suffixes=("", "_locacion")
    )

    # JOIN: rondas con turnos completos
    df_rondas_completo = df_rondas.merge(
        df_turnos_completo, left_on="turno_id", right_on="id", suffixes=("", "_turno")
    )

    # JOIN: incidentes con turnos completos
    df_incidentes_completo = df_incidentes.merge(
        df_turnos_completo, left_on="turno_id", right_on="id", suffixes=("", "_turno")
    )

    print("JOINs realizados:")
    print(f"  - Turnos completos: {len(df_turnos_completo)} registros")
    print(f"  - Rondas completas: {len(df_rondas_completo)} registros")
    print(f"  - Incidentes completos: {len(df_incidentes_completo)} registros")

    return df_turnos_completo, df_rondas_completo, df_incidentes_completo
