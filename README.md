# PythonMaestria — Framework de Análisis Predictivo para Sermukai

MVP de un flujo *end-to-end* de machine learning en Python que convierte datos operativos desordenados en análisis predictivos para la toma de decisiones de la junta directiva de **Sermukai**, empresa de outsourcing de servicios de seguridad, limpieza y jardinería en Jalisco, México.

> **Pregunta detonante:** ¿Cómo puede un framework modular de machine learning en Python transformar datos empresariales desordenados en análisis predictivos confiables para apoyar decisiones estratégicas?

Este documento describe el notebook [`notebooks/avance_de_proyecto_2_modular.ipynb`](notebooks/avance_de_proyecto_2_modular.ipynb) y el paquete `sermukai/` que ejecuta.

---

## Estructura del repositorio

```
PythonMaestria/
├── data/                  # CSVs de entrada (datos operativos)
├── docs/                  # Documentación de contexto del proyecto
├── notebooks/
│   ├── avance_de_proyecto_2_modular.ipynb   # Notebook documentado aquí
│   └── avance_de_proyecto_2.ipynb           # Versión anterior (todo el código en el notebook)
└── sermukai/              # Paquete con la lógica del framework
    ├── __init__.py        # Expone PipelineSermukai
    ├── pipeline.py        # Clase orquestadora
    ├── carga.py           # Lectura de CSVs y JOINs
    ├── limpieza.py        # Limpieza y preprocesamiento
    ├── modelos.py         # IsolationForest y clasificador por keywords
    ├── metricas.py        # Validación del clasificador (F1 macro, MAE)
    ├── evaluacion.py      # Resumen estadístico de resultados
    └── visualizacion.py   # Heatmap y boxplot
```

La versión **modular** separa la lógica del notebook: todo el código vive en `sermukai/` y el notebook solo llama a las etapas del pipeline, una por una.

---

## Requisitos

- Python 3.10+
- `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `jupyter`

```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter
```

## Cómo ejecutarlo

```bash
cd notebooks
jupyter notebook avance_de_proyecto_2_modular.ipynb
```

Después, ejecuta las celdas en orden. El notebook agrega la raíz del proyecto a `sys.path` para importar `sermukai`, y el paquete encuentra la carpeta `data/` por su propia ruta, así que no depende del directorio de trabajo.

También se puede correr todo el flujo desde Python sin el notebook:

```python
from sermukai import PipelineSermukai

pipeline = PipelineSermukai(semilla=42).ejecutar()
```

---

## Datos de entrada (`data/`)

| Archivo | Columnas | Descripción |
|---|---|---|
| `empleados.csv` | `id, nombre, puesto, turno, edad` | Personal operativo |
| `locaciones.csv` | `id, nombre, direccion, nivel_riesgo` | Sitios atendidos y su nivel de riesgo |
| `turnos.csv` | `id, empleado_id, locacion_id, hora_inicio, hora_fin, estado` | Turnos asignados (empleado ↔ locación) |
| `rondas.csv` | `id, turno_id, hora_inicio, hora_final, duracion_esperada_min` | Rondas de vigilancia realizadas en cada turno |
| `incidentes.csv` | `id, turno_id, fecha_hora, notas, categoria, severidad` | Incidentes reportados; `categoria` y `severidad` pueden venir vacías |

`incidentes_original.csv` es una copia anterior de los incidentes y el pipeline no la usa.

**Relaciones:** `turnos → empleados` (por `empleado_id`), `turnos → locaciones` (por `locacion_id`), y `rondas`/`incidentes → turnos` (por `turno_id`).

---

## Flujo del notebook

La clase `PipelineSermukai` (`sermukai/pipeline.py`) guarda el estado entre etapas como atributos. Cada método regresa `self`, así que las etapas se pueden encadenar.

```
cargar → unir → limpiar → preprocesar → detectar_anomalias
       → clasificar_incidentes → validar_clasificador → evaluar
       → graficar_heatmap → graficar_boxplot
```

| Celda | Método | Módulo | Qué hace |
|---|---|---|---|
| 1 | `PipelineSermukai(semilla=42)` | `pipeline` | Crea el pipeline, fija la semilla de NumPy para que los resultados sean reproducibles y configura el estilo de las gráficas. |
| 2 | `cargar()` | `carga.load_data` | Lee los 5 CSVs y convierte a `datetime` las columnas de fecha. Resultado: `pipeline.dataframes`. |
| 3 | `unir()` | `carga.join_data` | JOINs: turnos + empleados + locaciones → `df_turnos_completo`; luego rondas e incidentes + turnos completos → `df_rondas_completo`, `df_incidentes_completo`. |
| 4 | `limpiar()` | `limpieza.data_cleanup` | Reporta nulos, elimina filas con nulos (excepto en `categoria` y `severidad`, que se rellenan después), elimina duplicados y reporta tipos de datos. |
| 5 | `preprocesar()` | `limpieza.pre_processing` | **Rondas:** calcula `duracion_real_min` y `desviacion_min` (real − esperada). **Incidentes:** extrae `dia_semana` y `hora`, y genera `notas_limpias` (en minúsculas y sin espacios sobrantes). |
| 6 | `detectar_anomalias()` | `modelos.detect_anomalies` | `IsolationForest` (`contamination=0.1`, `n_estimators=100`, `random_state=42`) sobre `desviacion_min`. Agrega la columna booleana `es_anomalia`. |
| 7 | `clasificar_incidentes()` | `modelos.classify_incidents` | Rellena `categoria` y `severidad` faltantes con reglas por keywords en las notas. Antes guarda los incidentes que ya venían etiquetados para validarlos en la siguiente celda. |
| 7b | `validar_clasificador()` | `metricas.validate_classifier` | Aplica las reglas a los incidentes que ya traían etiqueta real y compara: **F1 macro** para la categoría y **MAE** para la severidad. Resultado: `pipeline.metricas_clasificador`. |
| 8 | `evaluar()` | `evaluacion.evaluate_results` | Resumen: % de rondas anómalas, desviación promedio (normales vs. anómalas), distribución de categorías y severidad, y el top 10 de locaciones con más incidentes. |
| 9 | `graficar_heatmap()` | `visualizacion.present_heatmap` | Heatmap de incidentes por día de la semana × hora (0–23). |
| 10 | `graficar_boxplot()` | `visualizacion.present_boxplot` | Boxplot de `desviacion_min` en las 10 locaciones con más rondas, con las anomalías de IsolationForest marcadas con ✕ rojas. |

### Detalle de los modelos

**Detección de anomalías (IsolationForest).** Es un modelo no supervisado: aísla los puntos que se separan fácilmente del resto. Con `contamination=0.1` se asume que alrededor del 10 % de las rondas son atípicas, ya sea porque duraron mucho más o mucho menos de lo esperado. No necesita reglas manuales ni datos etiquetados.

**Clasificación de incidentes por keywords.** Hay una lista de reglas (`REGLAS` en `modelos.py`) donde cada grupo de palabras clave se asocia con una categoría y una severidad de 1 a 5. Gana la primera regla que coincide con la nota. Si ninguna coincide, el incidente queda como `"Sin clasificar"` con severidad 1. Las etiquetas que ya existían se conservan.

Ejemplos de reglas:

| Keywords | Categoría | Severidad |
|---|---|---|
| alarma, intrusión | Alarma activada | 4 |
| humo, incendio, fuego | Incendio | 5 |
| altercado, verbal, conflicto | Altercado | 4 |
| grafiti, muro | Vandalismo | 2 |
| animal, silvestre | Otro | 1 |

**Métricas de validación.**
- **F1 macro (categoría):** promedia el F1 de cada clase con el mismo peso, así que las clases raras (p. ej. *Altercado*) cuentan igual que las frecuentes.
- **MAE (severidad):** error absoluto medio en niveles de la escala 1–5. Confundir un 1 con un 5 penaliza más que confundir un 4 con un 5.

Escala de severidad: 1 Muy baja · 2 Baja · 3 Media · 4 Alta · 5 Crítica.

---

## Conclusiones del análisis

**Heatmap (concentración de incidentes)**
- Hay más incidentes en el horario nocturno (20:00–03:00), lo que es consistente con la operación de seguridad.
- Viernes y sábado tienen un aumento notable, lo que sugiere reforzar al personal en esas franjas.
- En el horario diurno hay menos actividad, lo que podría justificar mover recursos hacia los turnos nocturnos.

**Boxplot (desviación de rondas)**
- Las locaciones con cajas más anchas tienen más variabilidad en la duración de sus rondas.
- Las anomalías (✕ rojas) son desviaciones significativas, tanto por exceso como por defecto.
- Las locaciones con nivel de riesgo alto que además tienen desviaciones frecuentes requieren atención especial.

**Valor del framework**
- IsolationForest detecta rondas atípicas de forma automática y escala conforme crecen los datos.
- Aunque es un enfoque simple de PLN, la clasificación por keywords permite llenar los vacíos de categoría y severidad.
- El flujo modular (carga → limpieza → preprocesamiento → análisis → evaluación → visualización) facilita el mantenimiento y la extensión del sistema.

## Siguientes pasos

1. Conectar con los datos reales de la base de datos de Sermukai.
2. Entrenar un modelo de PLN para clasificar los incidentes con más precisión.
3. Implementar alertas automáticas cuando se detecten anomalías en tiempo real.
4. Desarrollar un dashboard interactivo para la junta directiva.
