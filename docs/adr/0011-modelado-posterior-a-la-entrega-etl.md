---
status: accepted
date: 2026-09-29
---

# Modelado posterior a la entrega de ETL

## Implementación vigente

La entrega 2 comprende preparación, análisis y copia candidata. El [notebook autónomo de entrega 3](../../temporal_version_tp_entrega03.ipynb) implementa el flujo de modelado. La referencia anterior se preservó con código/salidas. Se amplió la decisión a dos escenarios: personas nuevas y futuras lecturas de pacientes conocidos. Se congeló y evaluó una vez el candidato para personas nuevas; la prueba temporal independiente de pacientes conocidos sigue pendiente. Estado y resultados en [entrega 3](../entrega-03/README.md).

## Decisión y motivo

Clasificación multiclase, no ordinal. Los mapas descriptivos no demuestran rendimiento predictivo. Separar implementado y ejecutado; comparar Dummy, logística, RF y XGB. Escalado y pesos solo se ajustan con entrenamiento.

Reservar aproximadamente 20 % de pacientes completos para test interno, semilla 42, sin compartir pacientes con desarrollo. Dentro de desarrollo, comparar cinco folds StratifiedGroupKFold por paciente frente a StratifiedKFold por epochs mezclados con configuraciones fijas. Conservar esta mezcla como diagnóstico, sin elegir por la cifra más alta entre protocolos. Por decisión explícita del usuario, seleccionar candidatos separados para personas nuevas y pacientes conocidos; no se consultó test. Ambos modelos predicen epochs, no cambia la unidad de predicción.

Personas nuevas: validación por pacientes separados. Pacientes conocidos: seis bloques cronológicos por persona, el primero inicializa entrenamiento y los cinco siguientes se evalúan con entrenamiento creciente; separar entrenamiento y validación por 15 minutos. Los epochs iniciales no tienen predicción OOF. Guardar elegibilidad, cobertura y asignaciones. El mismo catálogo de variantes se evalúa dentro de ambos escenarios; cada escenario tiene su propia selección.

El escenario conocido presupone observaciones pasadas etiquetadas disponibles para entrenar; recibir señales pasadas sin anotaciones no implica que el modelo conozca a esa persona. Las etiquetas de entrenamiento no se incorporan como características de historia durante inferencia.

Contexto temporal: señales anteriores del mismo paciente y segmento continuo, nunca etiquetas reales previas ni datos futuros. Historia ausente se conserva como NaN con indicador de disponibilidad; imputación aprendida dentro del entrenamiento. SMOTE se prueba por separado y únicamente dentro del entrenamiento. Reglas de balanceo en [ADR 0009](0009-distribuciones-y-desbalance-de-etapas.md).

El test interno tuvo exposición en EDA y comparaciones previas: declarar esta limitación. Congelar configuración, reentrenar con todo desarrollo y evaluar sin reajuste posterior. Guardar marcador persistente con estados reservado/abierto/evaluado: un estado incompleto bloquea reintentos automáticos; resultados completos se verifican mediante huellas y se leen sin entrenar ni inferir de nuevo. Persistir probabilidades y clases antes de calcular métricas, que se reconstruyen desde ese archivo. Guardar pipeline con imputación y modelo, comprobar serialización en desarrollo y conservar configuración/columnas/versiones congeladas. Pacientes adicionales futuros permitirán evaluación externa separada. Detalle operativo en el README de entrega 3.

## Alternativas y criterio de comparación

Una división única por paciente es más económica, pero depende más de los pacientes asignados; `GroupKFold` mantiene separados los pacientes sin intentar conservar las proporciones de etapas. Se conserva StratifiedGroupKFold para personas desconocidas y validación cronológica para el futuro de personas conocidas. No hay ganador universal entre ambas preguntas.

El clasificador trivial permite saber qué se logra sin distinguir etapas; regresión logística multiclase ofrece una referencia inicial y Random Forest/XGBoost permiten contrastar relaciones no lineales e interacciones. Son candidatos, no ganadores aprobados ni requisitos específicos de la cátedra.

Comparar escenarios y representaciones con las mismas particiones del protocolo elegido. La validación orienta modelos, parámetros y características; reservar la prueba para la evaluación final acordada. Informar F1 macro, matriz de confusión, precisión/recuperación por etapa y variación entre pacientes. La elección debe considerar desempeño y disponibilidad real de señales, especialmente si se propone usar solo wearable.

Guardar predicciones y probabilidades de validación por fold, configuración y escenario: cada epoch elegible se predice una vez por un modelo que no entrenó con su etiqueta. Solo el protocolo por pacientes garantiza no haber entrenado con su persona; el cronológico utiliza únicamente su pasado. La matriz acumulada y las curvas Precision-Recall complementan métricas por etapa, fold y paciente. El test reservado por personas evalúa el primer escenario y no constituye una prueba cronológica independiente para personas conocidas. Detalle en [entrega 3](../entrega-03/README.md#qué-mirar).

## Alcance

La consigna disponible ubica selección de técnicas, parámetros, evaluación e interpretación en la tercera entrega. El detalle operativo está en [entrega 3](../entrega-03/README.md); ningún algoritmo queda elegido como ganador antes de medirlo.
