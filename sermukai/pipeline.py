"""Clase que orquesta el flujo completo y conserva el estado entre etapas."""

import numpy as np

from .carga import RUTA_DATOS, load_data, join_data
from .limpieza import data_cleanup, pre_processing
from .modelos import detect_anomalies, classify_incidents
from .evaluacion import evaluate_results
from .metricas import validate_classifier
from .visualizacion import configurar_visualizacion, present_heatmap, present_boxplot


class PipelineSermukai:
    """
    Flujo end-to-end: carga → JOINs → limpieza → preprocesamiento →
    anomalías → clasificación → evaluación → visualización.

    Cada etapa se puede ejecutar por separado (en el orden indicado) o todas
    juntas con `ejecutar()`. Los DataFrames resultantes quedan como atributos.
    """

    def __init__(self, ruta=RUTA_DATOS, semilla=42):
        self.ruta = ruta
        # Semilla para reproducibilidad: sin ella cada ejecución podría marcar
        # rondas distintas con anomalías y sería difícil comparar resultados.
        np.random.seed(semilla)
        configurar_visualizacion()

        self.dataframes = None
        self.df_turnos_completo = None
        self.df_rondas_completo = None
        self.df_incidentes_completo = None
        self.df_rondas_proc = None
        self.df_incidentes_proc = None
        self.df_incidentes_etiquetados = None
        self.metricas_clasificador = None

    def cargar(self):
        self.dataframes = load_data(self.ruta)
        return self

    def unir(self):
        (self.df_turnos_completo,
         self.df_rondas_completo,
         self.df_incidentes_completo) = join_data(self.dataframes)
        return self

    def limpiar(self):
        self.df_rondas_completo = data_cleanup(self.df_rondas_completo, "Rondas (con JOIN)")
        self.df_incidentes_completo = data_cleanup(self.df_incidentes_completo, "Incidentes (con JOIN)")
        return self

    def preprocesar(self):
        self.df_rondas_proc, self.df_incidentes_proc = pre_processing(
            self.df_rondas_completo, self.df_incidentes_completo
        )
        return self

    def detectar_anomalias(self):
        self.df_rondas_proc = detect_anomalies(self.df_rondas_proc)
        return self

    def clasificar_incidentes(self):
        # Guardar los incidentes que ya traían etiqueta real, antes de rellenar el resto
        self.df_incidentes_etiquetados = self.df_incidentes_proc.dropna(
            subset=["categoria", "severidad"]
        )
        self.df_incidentes_proc = classify_incidents(self.df_incidentes_proc)
        return self

    def validar_clasificador(self):
        self.metricas_clasificador = validate_classifier(self.df_incidentes_etiquetados)
        return self

    def evaluar(self):
        evaluate_results(self.df_rondas_proc, self.df_incidentes_proc)
        return self

    def graficar_heatmap(self):
        present_heatmap(self.df_incidentes_proc)
        return self

    def graficar_boxplot(self):
        present_boxplot(self.df_rondas_proc)
        return self

    def ejecutar(self):
        """Corre todas las etapas en orden."""
        return (self.cargar().unir().limpiar().preprocesar()
                .detectar_anomalias().clasificar_incidentes().validar_clasificador().evaluar()
                .graficar_heatmap().graficar_boxplot())
