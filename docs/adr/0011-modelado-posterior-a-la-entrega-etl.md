---
status: accepted
date: 2026-09-29
---

# Modelado posterior a la entrega de ETL

## Implementación vigente

La entrega 2 comprende preparación, análisis y copia candidata. La sección 4 plantea modelos y evaluación para continuar; no hay entrenamiento ni métricas predictivas en el notebook actual. La consigna disponible incluye modelado, evaluación e interpretación en la entrega 3.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Cerrar la preparación antes de atribuir resultados a modelos. Los mapas descriptivos y controles de integridad no demuestran precisión predictiva. La sección 4 presenta propuestas, no entrenamientos ejecutados.

La tarea futura es clasificación multiclase, no ordinal. Comparar referencia trivial, regresión logística multiclase, Random Forest y XGBoost con particiones por paciente. Escalado, selección y posibles pesos se ajustan dentro de entrenamiento; validación orienta decisiones y la prueba final se reserva.

Se acuerda usar `StratifiedGroupKFold` con pacientes como grupos para evitar compartir personas entre entrenamiento y validación e intentar conservar las proporciones de etapas. La validación cruzada permite comparar modelos en varios conjuntos de pacientes, reduciendo la dependencia de una única división. La estratificación no balancea clases ni garantiza cobertura suficiente de cada etapa; debe comprobarse antes de entrenar. Esta estrategia está acordada, aún pendiente de implementación y verificación; el detalle operativo se mantiene en el [README de entrega 3](../entrega-03/README.md#objetivo-y-evaluación-acordados).

## Alternativas y criterio de comparación

Una división única por paciente es más económica, pero depende más de los pacientes asignados; `GroupKFold` mantiene separados los pacientes sin intentar conservar las proporciones de etapas. Se prioriza `StratifiedGroupKFold` por el desbalance y la presencia desigual de etapas entre personas.

El clasificador trivial permite saber qué se logra sin distinguir etapas; regresión logística multiclase ofrece una referencia inicial y Random Forest/XGBoost permiten contrastar relaciones no lineales e interacciones. Son candidatos, no ganadores aprobados ni requisitos específicos de la cátedra.

Comparar escenarios y representaciones con las mismas particiones por paciente. La validación orienta modelos, parámetros y características; reservar la prueba para la evaluación final acordada. Informar F1 macro, matriz de confusión, precisión/recuperación por etapa y variación entre pacientes. La elección debe considerar desempeño y disponibilidad real de señales, especialmente si se propone usar solo wearable.

Guardar predicciones y probabilidades de validación por fold, configuración y escenario para el diagnóstico global: cada epoch se predice una vez por un modelo que no entrenó con su paciente. La matriz acumulada y las curvas Precision-Recall complementan métricas por etapa, fold y paciente; no prueban generalización final ni describen por sí solas transiciones temporales. Su construcción se especifica en [entrega 3](../entrega-03/README.md#diagnóstico-global-por-modelo).

## Alcance

La consigna disponible ubica selección de técnicas, parámetros, evaluación e interpretación en la tercera entrega. El detalle operativo está en [entrega 3](../entrega-03/README.md); ningún algoritmo queda elegido como ganador antes de medirlo.
