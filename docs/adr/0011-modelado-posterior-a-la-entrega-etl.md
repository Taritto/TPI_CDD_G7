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

La tarea futura es clasificación multiclase, no ordinal. Comparar referencia trivial, regresión logística multiclase y un modelo de árboles con particiones por paciente. Escalado, selección y posibles pesos se ajustan dentro de entrenamiento; validación orienta decisiones y la prueba final se reserva.

## Alternativas y criterio de comparación

El clasificador trivial permite saber qué se logra sin distinguir etapas; regresión logística multiclase ofrece una referencia inicial y un modelo de árboles permite contrastar relaciones no lineales. Son candidatos, no ganadores aprobados ni requisitos específicos de la cátedra.

Comparar escenarios y representaciones con las mismas particiones por paciente. La validación orienta modelos, parámetros y características; reservar la prueba para la evaluación final acordada. Informar F1 macro, matriz de confusión, precisión/recuperación por etapa y variación entre pacientes. La elección debe considerar desempeño y disponibilidad real de señales, especialmente si se propone usar solo wearable.

## Alcance

La consigna disponible ubica selección de técnicas, parámetros, evaluación e interpretación en la tercera entrega. El detalle operativo está en [entrega 3](../entrega-03/README.md); ningún algoritmo queda elegido como ganador antes de medirlo.
