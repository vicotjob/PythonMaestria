"""Visualizaciones: heatmap de incidentes y boxplot de desviación de rondas."""

import matplotlib.pyplot as plt
import seaborn as sns


def configurar_visualizacion():
    """Aplica la configuración global de matplotlib y seaborn."""
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['figure.dpi'] = 100
    sns.set_style("whitegrid")


def present_heatmap(df_incidentes):
    """
    Genera un heatmap que muestra la concentración de incidentes por día y hora.

    Recibe: DataFrame de incidentes con columnas 'dia_semana' y 'hora'.
    Devuelve: Nada (renderiza la gráfica).
    """
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    pivot = df_incidentes.pivot_table(
        index="dia_semana",
        columns="hora",
        values="id",
        aggfunc="count",
        fill_value=0
    )

    # Reindexar para asegurar orden correcto y todas las horas
    pivot = pivot.reindex(index=orden_dias, fill_value=0)
    todas_horas = list(range(24))
    pivot = pivot.reindex(columns=todas_horas, fill_value=0)

    fig, ax = plt.subplots(figsize=(16, 6))
    sns.heatmap(
        pivot,
        cmap="YlOrRd",
        annot=True,
        fmt="d",
        linewidths=0.5,
        cbar_kws={"label": "Cantidad de incidentes"},
        ax=ax
    )

    ax.set_title("Concentración de Incidentes por Día de la Semana y Hora del Día",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Hora del día (0-23)", fontsize=12)
    ax.set_ylabel("Día de la semana", fontsize=12)

    plt.tight_layout()
    plt.show()


def present_boxplot(df_rondas):
    """
    Genera un boxplot que muestra la desviación de duración de rondas por locación.
    Muestra las 10 locaciones con más rondas para mantener la legibilidad.

    Recibe: DataFrame de rondas con columnas 'desviacion_min', 'nombre_locacion' y 'es_anomalia'.
    Devuelve: Nada (renderiza la gráfica).
    """
    # Determinar la columna de nombre de locación
    if "nombre_locacion" in df_rondas.columns:
        col_loc = "nombre_locacion"
    else:
        col_loc = "nombre_turno"

    # Filtrar a las 10 locaciones con más rondas
    top_locaciones = df_rondas[col_loc].value_counts().head(10).index
    df_filtrado = df_rondas[df_rondas[col_loc].isin(top_locaciones)]

    fig, ax = plt.subplots(figsize=(16, 7))

    sns.boxplot(
        data=df_filtrado,
        x=col_loc,
        y="desviacion_min",
        palette="Set2",
        ax=ax,
        fliersize=4
    )

    # Superponer puntos de anomalías detectadas
    anomalas = df_filtrado[df_filtrado["es_anomalia"]]
    if len(anomalas) > 0:
        sns.stripplot(
            data=anomalas,
            x=col_loc,
            y="desviacion_min",
            color="red",
            size=8,
            marker="X",
            alpha=0.7,
            ax=ax,
            label="Anomalía (IsolationForest)"
        )

    ax.set_title("Desviación de Duración de Rondas por Locación (Top 10)\n(Real vs Esperada)",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Locación", fontsize=12)
    ax.set_ylabel("Desviación en minutos (real - esperada)", fontsize=12)
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5, label="Sin desviación")

    plt.xticks(rotation=30, ha="right")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.show()
