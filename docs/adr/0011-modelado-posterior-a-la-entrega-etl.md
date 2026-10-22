---
status: accepted
date: 2026-09-29
---

# Modelado posterior a la entrega de ETL

## Implementación vigente

La entrega 2 comprende preparación, análisis y copia candidata. El [notebook oficial de entrega 3](../../temporal_version_tp_entrega03.ipynb) queda como referencia mientras el equipo revisa la [copia con los ajustes acordados](../../temporal_version_tp_entrega03_revision.ipynb). Los resultados y el estado de ejecución de esa copia se documentan en [entrega 3](../entrega-03/README.md).

La revisión retira la evaluación cronológica y la propuesta solo wearable. Conserva el código y las salidas de la antigua 4.8 como evaluación histórica. La fecha del ADR registra la decisión original y se conserva; estas modificaciones reflejan las decisiones posteriores aprobadas por el equipo.

## Decisión y motivo

Identificar la etapa del epoch actual de 30 segundos con wearable + PSG. Es clasificación multiclase categórica; las asociaciones descriptivas no demuestran capacidad predictiva. Comparar Dummy, logística, RF y XGBoost. Ningún algoritmo se considera ganador antes de medirlo.

Conservar la asignación de aproximadamente 20 % de pacientes al test interno, semilla 42. Estos 16 pacientes ya se evaluaron y no se usan para nuevos ajustes. Dentro de los 60 pacientes de desarrollo, seleccionar un candidato con cinco folds de StratifiedGroupKFold agrupados por patient_id y otro con cinco folds de StratifiedKFold por epochs mezclados. Cada protocolo reutiliza sus propias particiones y el mismo catálogo de alternativas.

Solo pacientes separados garantiza que el modelo de cada fold no entrenó con esa persona. Epochs mezclados puede compartir sujetos y observaciones próximas: sus cifras no demuestran mejor generalización a pacientes nuevos. Se conservan ambos candidatos para compararlos sobre las mismas personas adicionales, fijando las configuraciones antes de acceder a esas nuevas etiquetas. La comparación contrasta candidatos concretos; no demuestra superioridad universal de un protocolo.

## Selección, características y balanceo

Variar un hiperparámetro por vez respecto de su referencia, sin producto cartesiano ni duplicados. Acotar la búsqueda a dos cambios individuales por algoritmo: RF (`max_depth=16`, `min_samples_leaf=10`) y XGBoost (`max_depth=2`, `reg_lambda=5`), en ambos protocolos y con/sin pesos. Logística permanece como referencia, sin búsqueda de C. Es una exploración acotada por costo, no una búsqueda exhaustiva. Después contrastar representaciones, contexto temporal y balanceo. Elegir por F1 macro promedio de validación; desempates por dispersión, tiempo y nombre. Conservar el mejor RF y XGBoost base para importancia por permutación; historia y balanceo parten de un único ganador base por protocolo.

Contexto temporal: señales pasadas del mismo paciente y segmento continuo, nunca etiquetas anteriores ni señales futuras. Una discontinuidad reinicia la historia; falta de antecedentes conserva NaN e indicador. La mediana se aprende dentro del entrenamiento. Al mezclar epochs, los retardos pueden compartir señales entre folds aunque sean causales.

Escalado, imputación, pesos y SMOTE se ajustan exclusivamente con entrenamiento. SMOTE se estudia sin historia ni pesos adicionales; validación y métricas de entrenamiento se calculan sobre observaciones reales. Reglas de balanceo en [ADR 0009](0009-distribuciones-y-desbalance-de-etapas.md).

## Diagnóstico y prueba adicional

Guardar una predicción y probabilidades OOF por epoch, configuración y protocolo. Distinguir promedio entre folds de métricas acumuladas. Informar F1 macro, precisión/recuperación/F1 por etapa, matrices, ROC-AUC y resultados por paciente con cobertura de etapas. Retirar Precision–Recall/AP de los diagnósticos activos; las salidas históricas quedan preservadas.

El test interno tuvo exposición en EDA y comparaciones previas: declarar esta limitación. Su evaluación histórica conserva código y resultados, sin reentrenar ni inferir allí. No transferir sus métricas a candidatos nuevos.

La comparación adicional requiere pacientes distintos de la cohorte histórica y CSV procesados con las mismas reglas del ETL. Ambos candidatos se entrenan con los mismos 60 pacientes de desarrollo y se evalúan en las mismas personas nuevas. No se reajusta a partir de esta prueba. Sin esas entradas, la comparación queda pendiente.

Conservar configuración, columnas, representación, retardos, balanceo, versiones y fuentes. Persistir pipelines, probabilidades y predicciones. Una ejecución adicional incompleta bloquea reintentos automáticos; una completada verifica huellas y se relee sin entrenar ni inferir. Guardar las nuevas exportaciones por separado de las históricas.

## Alternativas y consecuencias

Una división única por paciente es más económica, pero depende más de las personas asignadas. GroupKFold mantiene grupos sin intentar conservar proporciones. StratifiedGroupKFold intenta distribuir etapas sin garantizar cobertura; comprobarla antes de entrenar. Estratificar no balancea clases.

La evaluación cronológica respondía al uso de pasado etiquetado para predecir períodos futuros del mismo paciente. Se retiró del alcance activo por decisión del equipo, conservando sus versiones anteriores en Git. Los retardos de señales siguen disponibles y no implican realizar ese protocolo de evaluación.

La selección sobre muchos candidatos puede optimizar en exceso los mismos folds; las diferencias pequeñas no prueban superioridad concluyente. La comparación adicional amplía la evidencia y debe reportar ambos resultados, incluso si el candidato seleccionado con epochs mezclados no mantiene su ventaja de validación.

## Alcance

La consigna ubica selección de técnicas, parámetros, evaluación e interpretación en la tercera entrega. La revisión mantiene únicamente wearable + PSG. El detalle operativo y los resultados efectivamente ejecutados viven en la documentación de la entrega; el ADR conserva las reglas y sus motivos.
