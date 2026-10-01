# Contexto para Agente: MVP del Framework de Análisis Predictivo — Sermukai

## Objetivo

Genera un Jupyter Notebook (.ipynb) que implemente el **happy path completo** del framework modular de machine learning descrito abajo. No se requiere la solución final con modelos entrenados en producción, sino un MVP funcional que demuestre el flujo end-to-end con datos simulados y que produzca las **dos visualizaciones** del plan de exploración (Heatmap y Boxplot).

---

## 1. Contexto del negocio

**Empresa:** Sermukai — outsourcing de servicios de seguridad, limpieza y jardinería en México (Jalisco).

**Problemática:** La empresa necesita visibilidad sobre las operaciones de sus guardias de seguridad: cumplimiento de turnos, duración de rondas, incidentes reportados, y detección temprana de anomalías para la toma de decisiones de la junta directiva.

**Pregunta detonante:** ¿Cómo puede un framework modular de machine learning en Python transformar datos empresariales desordenados en análisis predictivos confiables para apoyar decisiones estratégicas?

---

## 2. Esquema de base de datos (5 tablas)

### Empleados
| Tipo      | Campo   | Restricción |
|-----------|---------|-------------|
| uuid      | id      | PK          |
| nvarchar  | nombre  |             |
| nvarchar  | puesto  |             |
| nvarchar  | turno   |             |
| int       | edad    |             |

### Locaciones
| Tipo      | Campo        | Restricción |
|-----------|--------------|-------------|
| uuid      | id           | PK          |
| nvarchar  | nombre       |             |
| nvarchar  | direccion    |             |
| int       | nivel_riesgo |             |

### Turnos
| Tipo      | Campo        | Restricción |
|-----------|--------------|-------------|
| uuid      | id           | PK          |
| uuid      | empleado_id  | FK → Empleados |
| uuid      | locacion_id  | FK → Locaciones |
| datetime  | hora_inicio  |             |
| datetime  | hora_fin     |             |
| nvarchar  | estado       |             |

### Rondas
| Tipo      | Campo                 | Restricción |
|-----------|-----------------------|-------------|
| uuid      | id                    | PK          |
| uuid      | turno_id              | FK → Turnos |
| datetime  | hora_inicio           |             |
| datetime  | hora_final            |             |
| int       | duracion_esperada_min |             |

### Incidentes
| Tipo      | Campo      | Restricción |
|-----------|------------|-------------|
| uuid      | id         | PK          |
| uuid      | turno_id   | FK → Turnos |
| datetime  | fecha_hora |             |
| nvarchar  | notas      |             |
| nvarchar  | categoria  |             |
| int       | severidad  |             |

---

## 3. Datos simulados de ejemplo

Usa estos registros como semilla y **amplíalos programáticamente** para tener suficiente volumen (~50-100 turnos, ~100-200 rondas, ~30-60 incidentes) distribuidos a lo largo de varias semanas y diferentes horas del día. Esto es necesario para que las visualizaciones sean significativas.

### Empleados (5 registros base)
```python
empleados = [
    {"id": "29aa57d8-4323-47af-b520-46ca372af4d0", "nombre": "Carlos García", "puesto": "Supervisor", "turno": "Matutino", "edad": 39},
    {"id": "107f2f15-084c-4f7e-bad6-4d5010d41d4e", "nombre": "María López", "puesto": "Guardia de seguridad", "turno": "Matutino", "edad": 28},
    {"id": "26a9f99a-764d-4053-a693-1503fe386703", "nombre": "Juan Hernández", "puesto": "Guardia de Seguridad", "turno": "Matutino", "edad": 27},
    {"id": "feb2f711-97d0-4a32-85bf-94a615060504", "nombre": "Ana Martínez", "puesto": "Supervisor", "turno": "Nocturno", "edad": 54},
    {"id": "a6e14b3d-98cc-4d90-92dd-c32a84bc159c", "nombre": "Pedro Rodríguez", "puesto": "Guardia de seguridad", "turno": "Nocturno", "edad": 34},
]
```

### Locaciones (5 registros base)
```python
locaciones = [
    {"id": "80ba3dfc-2b83-4307-b116-853e48e46533", "nombre": "Plaza comercial galerías", "direccion": "Av. Vallarta 3959, Zapopan, Jalisco", "nivel_riesgo": 1},
    {"id": "bd9f3ac2-e21d-40dc-b179-09e7a41e8d67", "nombre": "Torre corporativa Andares", "direccion": "Blvd. Puerta de Hierro 4965, Zapopan, Jalisco", "nivel_riesgo": 3},
    {"id": "e90449da-d10b-48ee-9b48-90089c366950", "nombre": "Hospital Regional IMSS", "direccion": "Belisario Domínguez 1000, Guadalajara, Jalisco", "nivel_riesgo": 3},
    {"id": "f77813d4-2982-4545-9501-76811094ee36", "nombre": "Centro de distribución Walmart", "direccion": "Carretera a El Salto Km 15, Tlajomulco, Jalisco", "nivel_riesgo": 2},
    {"id": "f7d9988e-09ed-4b6c-aab4-bf55eaf2d82e", "nombre": "Parque Industrial Tecnológico", "direccion": "Av. del Bosque 1001, Zapopan, Jalisco", "nivel_riesgo": 1},
]
```

### Notas de incidentes de ejemplo (para ampliar con variaciones)
```python
notas_ejemplo = [
    "Se activó la alarma de intrusión en la zona 2 sin causa aparente.",
    "Persona sospechosa merodeando cerca de la entrada principal alrededor de las 9:30 PM.",
    "Guardia reportó ruidos extraños en el estacionamiento nivel 2.",
    "Se encontró puerta de emergencia abierta sin autorización.",
    "Vehículo no identificado estacionado en zona restringida durante la madrugada.",
    "Falla en cámara de vigilancia del pasillo norte, se reportó a mantenimiento.",
    "Individuo intentó ingresar con identificación vencida.",
    "Se detectó fuga de agua en el cuarto de vigilancia.",
    "Altercado verbal entre dos personas en el estacionamiento.",
    "Guardia no se presentó a la ronda programada de las 3 AM.",
]
```

**Importante para la generación de datos:** Al ampliar los datos, introduce intencionalmente:
- Algunas rondas con duración real mucho menor o mayor que la esperada (anomalías).
- Mayor concentración de incidentes en ciertos días/horas (para que el heatmap sea interesante).
- Algunos campos `categoria` y `severidad` como `None`/`NaN` (reflejando que aún no se clasifican).

---

## 4. Flujo del happy path (módulos a implementar)

Cada módulo debe ser una función con docstring. Seguir el principio de Single Responsibility.

### 4.1 `load_data()` — Carga de datos
- **Entrada:** Ninguna (genera los DataFrames internamente con datos simulados ampliados).
- **Proceso:** Crea los 5 DataFrames (empleados, locaciones, turnos, rondas, incidentes) con datos simulados amplificados usando `uuid4()`, `random`, y `datetime`. Hacer los JOINs necesarios.
- **Salida:** Diccionario con los DataFrames: `{"empleados": df, "locaciones": df, "turnos": df, "rondas": df, "incidentes": df}` y un DataFrame consolidado con JOINs.

### 4.2 `data_cleanup(df)` — Validación y limpieza
- **Entrada:** DataFrame(s) generado(s).
- **Proceso:** Detectar nulos, duplicados, inconsistencias de tipo. Reportar cuántos registros se limpiaron.
- **Salida:** DataFrame(s) limpio(s) + resumen de limpieza impreso.

### 4.3 `pre_processing(df)` — Preprocesamiento
- **Entrada:** DataFrame validado.
- **Proceso:**
  - Calcular `duracion_real_min` = (hora_final - hora_inicio) en minutos para rondas.
  - Calcular `desviacion_min` = duracion_real_min - duracion_esperada_min.
  - Extraer `dia_semana` y `hora` de `fecha_hora` en incidentes.
  - Limpieza básica del campo `notas` (lowercase, strip).
- **Salida:** DataFrames enriquecidos listos para análisis.

### 4.4 `detect_anomalies(df_rondas)` — Detección de anomalías
- **Entrada:** DataFrame de rondas preprocesado.
- **Proceso:** Usar `IsolationForest` de scikit-learn sobre la columna de desviación de duración para marcar rondas anómalas.
- **Salida:** DataFrame con columna `es_anomalia` (bool).

### 4.5 `classify_incidents(df_incidentes)` — Clasificación básica de incidentes (PLN simplificado)
- **Entrada:** DataFrame de incidentes con notas limpias.
- **Proceso:** Clasificación basada en reglas/keywords (para el MVP, no requiere modelo entrenado). Asignar categoría y severidad estimada donde sean nulos.
- **Salida:** DataFrame con `categoria` y `severidad` rellenados.

### 4.6 `evaluate_results(...)` — Evaluación básica
- **Entrada:** Resultados de anomalías y clasificación.
- **Proceso:** Resumen estadístico: cuántas anomalías detectadas, distribución de categorías, distribución de severidad.
- **Salida:** Métricas impresas.

### 4.7 `present_results(...)` — Visualizaciones finales
- **Entrada:** DataFrames procesados.
- **Proceso:** Generar las dos visualizaciones requeridas (ver sección 5).
- **Salida:** Gráficas renderizadas en el notebook.

---

## 5. Visualizaciones requeridas (OBLIGATORIAS)

### 5.1 Heatmap — Concentración de incidentes por día de la semana vs hora
- **Eje X:** Hora del día (0-23).
- **Eje Y:** Día de la semana (Lunes a Domingo).
- **Color:** Cantidad de incidentes en esa combinación.
- **Librería sugerida:** `seaborn.heatmap` o `matplotlib.pyplot.imshow`.
- **Propósito de negocio:** Si hay actividad elevada en horarios nocturnos ciertos días, justificar refuerzo de personal.

### 5.2 Boxplot — Desviación de duración de rondas (real vs esperada) por locación
- **Eje X:** Nombre de la locación.
- **Eje Y:** Desviación en minutos (duracion_real_min - duracion_esperada_min).
- **Librería sugerida:** `seaborn.boxplot` o `matplotlib.pyplot.boxplot`.
- **Propósito de negocio:** Cajas anchas señalan locaciones con rondas más irregulares.

---

## 6. Librerías a utilizar

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
import uuid
import random
from datetime import datetime, timedelta
```

---

## 7. Estructura esperada del notebook

1. **Celda 1 — Imports y configuración**
2. **Celda 2 — Generación de datos simulados** (amplificar los datos semilla a volumen suficiente)
3. **Celda 3 — `load_data()`** (cargar en DataFrames, hacer JOINs)
4. **Celda 4 — `data_cleanup()`** (validación, reporte de limpieza)
5. **Celda 5 — `pre_processing()`** (cálculos de duración, extracción de día/hora, limpieza de texto)
6. **Celda 6 — `detect_anomalies()`** (IsolationForest sobre desviaciones de rondas)
7. **Celda 7 — `classify_incidents()`** (clasificación por keywords del campo notas)
8. **Celda 8 — `evaluate_results()`** (resumen estadístico)
9. **Celda 9 — `present_results()`** — **Heatmap** de incidentes (día × hora)
10. **Celda 10 — `present_results()`** — **Boxplot** de desviación de rondas por locación
11. **Celda 11 — Conclusiones** (celda markdown con hallazgos)

---

## 8. Criterios de calidad del código

- Nombres de funciones descriptivos en snake_case.
- Docstrings en cada función (qué recibe, qué hace, qué devuelve).
- Principio de Single Responsibility: una función, una tarea.
- Manejo básico de errores con try/except donde sea crítico.
- Comentarios en español (el proyecto es para una maestría en Tecmilenio, México).
- Las visualizaciones deben tener títulos, etiquetas de ejes y leyendas en español.
- Usar `random.seed(42)` y `np.random.seed(42)` para reproducibilidad.

---

## 9. Lo que NO se requiere en el MVP

- No se requiere conexión a base de datos real (todo con DataFrames en memoria).
- No se requiere un modelo PLN entrenado (la clasificación por keywords es suficiente).
- No se requiere interfaz de usuario ni dashboard interactivo.
- No se requiere pipeline de CI/CD ni estructura de paquete.
- No se requiere que los modelos sean precisos; el objetivo es demostrar el flujo completo.
