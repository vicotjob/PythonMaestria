"""Validación, limpieza y preprocesamiento de datos."""


def data_cleanup(df, nombre_df="DataFrame", columnas_nulos_permitidos=("categoria", "severidad")):
    """
    Detecta y elimina nulos y duplicados, y reporta los tipos de datos de un DataFrame.

    Recibe: DataFrame, su nombre descriptivo y las columnas cuyos nulos NO se eliminan
            (por defecto 'categoria' y 'severidad', que se rellenan en la clasificación).
    Devuelve: DataFrame limpio y resumen de limpieza impreso.
    """
    print(f"\n{'='*50}")
    print(f"Limpieza de: {nombre_df} ({len(df)} registros)")
    print(f"{'='*50}")

    # Detectar nulos
    nulos = df.isnull().sum()
    nulos_total = nulos.sum()
    if nulos_total > 0:
        print(f"\nValores nulos encontrados ({nulos_total} total):")
        for col, count in nulos[nulos > 0].items():
            print(f"  - {col}: {count} nulos ({count/len(df)*100:.1f}%)")

        # Eliminar filas con nulos, salvo en las columnas que se rellenarán más adelante
        columnas_evaluar = [c for c in df.columns if c not in columnas_nulos_permitidos]
        antes = len(df)
        df = df.dropna(subset=columnas_evaluar)
        print(f"  → Filas con nulos eliminadas: {antes - len(df)}. Registros restantes: {len(df)}")
        print(f"  → Nulos conservados en: {[c for c in columnas_nulos_permitidos if c in df.columns]}")
    else:
        print("\nSin valores nulos.")

    # Detectar duplicados
    duplicados = df.duplicated().sum()
    if duplicados > 0:
        print(f"\nDuplicados encontrados: {duplicados}")
        df = df.drop_duplicates()
        print(f"  → Eliminados. Registros restantes: {len(df)}")
    else:
        print(f"Sin duplicados.")

    # Verificar tipos de datos
    print(f"\nTipos de datos:")
    for col, dtype in df.dtypes.items():
        print(f"  - {col}: {dtype}")

    return df


def pre_processing(df_rondas, df_incidentes):
    """
    Enriquece los DataFrames con columnas calculadas para el análisis.

    Recibe: DataFrames de rondas e incidentes (con JOINs).
    Devuelve: DataFrames enriquecidos con duración real, desviación, día de semana y hora.
    """
    # --- Rondas: calcular duración real y desviación ---
    df_rondas = df_rondas.copy()
    df_rondas["duracion_real_min"] = (
        (df_rondas["hora_final"] - df_rondas["hora_inicio"]).dt.total_seconds() / 60
    )
    df_rondas["desviacion_min"] = df_rondas["duracion_real_min"] - df_rondas["duracion_esperada_min"]

    print("Rondas preprocesadas:")
    print(f"  - Duración real promedio: {df_rondas['duracion_real_min'].mean():.1f} min")
    print(f"  - Desviación promedio: {df_rondas['desviacion_min'].mean():.1f} min")
    print(f"  - Desviación máxima: {df_rondas['desviacion_min'].max():.1f} min")

    # --- Incidentes: extraer día de semana y hora ---
    df_incidentes = df_incidentes.copy()
    dias_semana = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
                   4: "Viernes", 5: "Sábado", 6: "Domingo"}
    df_incidentes["dia_semana"] = df_incidentes["fecha_hora"].dt.weekday.map(dias_semana)
    df_incidentes["hora"] = df_incidentes["fecha_hora"].dt.hour

    # Limpieza básica de notas
    df_incidentes["notas_limpias"] = df_incidentes["notas"].str.lower().str.strip()

    print(f"\nIncidentes preprocesados:")
    print(f"  - Distribución por día: {df_incidentes['dia_semana'].value_counts().to_dict()}")

    return df_rondas, df_incidentes
