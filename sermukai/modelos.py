"""Modelos: detección de anomalías y clasificación de incidentes."""

import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(df_rondas):
    """
    Usa IsolationForest para detectar rondas con desviaciones anómalas de duración.

    Recibe: DataFrame de rondas con columna 'desviacion_min'.
    Devuelve: DataFrame con columna 'es_anomalia' (True/False).
    """
    df_rondas = df_rondas.copy()

    modelo = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
    predicciones = modelo.fit_predict(df_rondas[["desviacion_min"]])

    # IsolationForest: -1 = anomalía, 1 = normal
    df_rondas["es_anomalia"] = predicciones == -1

    total = len(df_rondas)
    anomalas = df_rondas["es_anomalia"].sum()
    print(f"Detección de anomalías completada:")
    print(f"  - Total de rondas: {total}")
    print(f"  - Rondas anómalas: {anomalas} ({anomalas/total*100:.1f}%)")
    print(f"  - Rondas normales: {total - anomalas} ({(total-anomalas)/total*100:.1f}%)")
    print(f"\nDesviación promedio en rondas anómalas: "
          f"{df_rondas.loc[df_rondas['es_anomalia'], 'desviacion_min'].mean():.1f} min")

    return df_rondas


# Reglas de clasificación: keyword → (categoría, severidad)
REGLAS = [
    (["alarma", "intrusión", "intrusion"], "Alarma activada", 4),
    (["sospechosa", "sospechoso", "merodeando"], "Persona sospechosa", 3),
    (["ruido", "extraño", "extraños"], "Actividad sospechosa", 2),
    (["puerta", "abierta", "emergencia"], "Acceso no autorizado", 3),
    (["vehículo", "vehiculo", "estacionado"], "Persona sospechosa", 2),
    (["cámara", "camara", "falla", "sistema"], "Falla eléctrica", 2),
    (["identificación", "identificacion", "ingresar", "sin identificación"], "Acceso no autorizado", 3),
    (["fuga", "agua", "rociadores"], "Daño a propiedad", 2),
    (["altercado", "verbal", "conflicto"], "Altercado", 4),
    (["ronda retrasada", "bloqueo", "retraso"], "Falla eléctrica", 1),
    (["humo", "incendio", "fuego"], "Incendio", 5),
    (["cortocircuito", "eléctrico", "tablero"], "Falla eléctrica", 4),
    (["grafiti", "grafitis", "muro"], "Vandalismo", 2),
    (["vidrio", "roto", "ventana"], "Daño a propiedad", 3),
    (["mareo", "médico", "apoyo médico"], "Emergencia médica", 3),
    (["pérdida", "equipo", "robo"], "Robo", 4),
    (["movimiento inusual", "movimiento"], "Intrusión perimetral", 4),
    (["animal", "silvestre"], "Otro", 1),
    (["evacuación", "evacuacion"], "Incendio", 4),
]


def predecir_con_reglas(nota):
    """Aplica las reglas por keywords a una nota. Devuelve (categoría, severidad)."""
    nota = nota if pd.notna(nota) else ""
    for keywords, cat, sev in REGLAS:
        if any(kw in nota for kw in keywords):
            return cat, sev
    return "Sin clasificar", 1


def classify_incidents(df_incidentes):
    """
    Clasifica incidentes usando reglas basadas en keywords del campo 'notas'.
    Rellena categoría y severidad donde sean nulos.

    Recibe: DataFrame de incidentes con columna 'notas_limpias'.
    Devuelve: DataFrame con 'categoria' y 'severidad' completados.
    """
    df = df_incidentes.copy()

    def clasificar_nota(row):
        if pd.notna(row["categoria"]) and pd.notna(row["severidad"]):
            return row["categoria"], row["severidad"]
        return predecir_con_reglas(row.get("notas_limpias"))

    resultados = df.apply(clasificar_nota, axis=1)
    df["categoria"] = resultados.apply(lambda x: x[0])
    df["severidad"] = resultados.apply(lambda x: x[1])

    nulos_antes = df_incidentes["categoria"].isnull().sum()
    sin_clasificar = (df["categoria"] == "Sin clasificar").sum()
    print(f"Clasificación de incidentes completada:")
    print(f"  - Incidentes sin categoría (antes): {nulos_antes}")
    print(f"  - Incidentes que ninguna regla pudo clasificar ('Sin clasificar'): {sin_clasificar}")
    print(f"\nDistribución de categorías:")
    print(df["categoria"].value_counts().to_string())

    return df
