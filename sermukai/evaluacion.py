"""Evaluación de resultados del análisis."""


def evaluate_results(df_rondas, df_incidentes):
    """
    Genera un resumen estadístico de los resultados del análisis.

    Recibe: DataFrames de rondas (con anomalías) e incidentes (clasificados).
    Devuelve: Nada (imprime métricas).
    """
    print("=" * 60)
    print("RESUMEN DE RESULTADOS DEL ANÁLISIS")
    print("=" * 60)

    # --- Anomalías en rondas ---
    total_rondas = len(df_rondas)
    anomalas = df_rondas["es_anomalia"].sum()
    print(f"\n📊 ANOMALÍAS EN RONDAS:")
    print(f"  Total de rondas analizadas: {total_rondas}")
    print(f"  Rondas anómalas detectadas: {anomalas} ({anomalas/total_rondas*100:.1f}%)")
    print(f"  Desviación promedio (normales): "
          f"{df_rondas.loc[~df_rondas['es_anomalia'], 'desviacion_min'].mean():.1f} min")
    print(f"  Desviación promedio (anómalas): "
          f"{df_rondas.loc[df_rondas['es_anomalia'], 'desviacion_min'].mean():.1f} min")

    # --- Distribución de categorías ---
    print(f"\n📊 DISTRIBUCIÓN DE CATEGORÍAS DE INCIDENTES:")
    categorias = df_incidentes["categoria"].value_counts()
    for cat, count in categorias.items():
        print(f"  - {cat}: {count} ({count/len(df_incidentes)*100:.1f}%)")

    # --- Distribución de severidad ---
    print(f"\n📊 DISTRIBUCIÓN DE SEVERIDAD:")
    severidades = df_incidentes["severidad"].value_counts().sort_index()
    etiquetas_sev = {1: "Muy baja", 2: "Baja", 3: "Media", 4: "Alta", 5: "Crítica"}
    for sev, count in severidades.items():
        etiqueta = etiquetas_sev.get(int(sev), f"Nivel {sev}")
        print(f"  - Severidad {int(sev)} ({etiqueta}): {count} incidentes")

    # --- Incidentes por locación ---
    if "nombre_locacion" in df_incidentes.columns:
        col_loc = "nombre_locacion"
    elif "nombre_turno" in df_incidentes.columns:
        col_loc = "nombre_turno"
    else:
        col_loc = None

    if col_loc:
        print(f"\n📊 INCIDENTES POR LOCACIÓN (top 10):")
        por_locacion = df_incidentes[col_loc].value_counts().head(10)
        for loc, count in por_locacion.items():
            print(f"  - {loc}: {count}")
