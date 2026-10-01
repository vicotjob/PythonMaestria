"""Validación del clasificador de incidentes con dos métricas: F1 macro y MAE."""

from sklearn.metrics import f1_score, mean_absolute_error

from .modelos import predecir_con_reglas


def validate_classifier(df_etiquetados):
    """
    Mide qué tan bien las reglas por keywords reproducen las etiquetas reales.

    Usa solo incidentes que ya traían 'categoria' y 'severidad' (verdad de referencia),
    ignora esas etiquetas al predecir y compara contra ellas.

    Métricas:
      - F1 macro (categoría): promedia el F1 de cada clase por igual, así las clases
        raras (p. ej. Altercado) pesan lo mismo que las frecuentes.
      - MAE (severidad): error promedio en niveles de la escala 1-5; confundir un 1
        con un 5 penaliza más que confundir un 4 con un 5.

    Recibe: DataFrame de incidentes con 'categoria', 'severidad' y 'notas_limpias'.
    Devuelve: diccionario con 'f1_macro', 'mae_severidad' y 'n_evaluados'.
    """
    df = df_etiquetados.dropna(subset=["categoria", "severidad"])
    predicciones = df["notas_limpias"].apply(predecir_con_reglas)
    cat_pred = predicciones.apply(lambda x: x[0])
    sev_pred = predicciones.apply(lambda x: x[1])

    f1 = f1_score(df["categoria"], cat_pred, average="macro", zero_division=0)
    mae = mean_absolute_error(df["severidad"], sev_pred)

    print("Validación del clasificador (reglas vs. etiquetas reales):")
    print(f"  - Incidentes evaluados: {len(df)}")
    print(f"  - F1 macro (categoría): {f1:.3f}")
    print(f"  - MAE (severidad, escala 1-5): {mae:.2f} niveles")

    return {"f1_macro": f1, "mae_severidad": mae, "n_evaluados": len(df)}
