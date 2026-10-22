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

Solo pacientes separados garantiza que el modelo de cada fold no entrenó con esa persona. Epochs mezclados puede compartir sujetos y observaciones próximas: sus cifras no demuestran mejor generalización a pacientes nuevos. Se conservan ambos candidatos para compararlos sobre los mismos 16 pacientes del test reservado, fijando las configuraciones antes de calcular nuevos resultados. El test ya fue consultado: comparación posterior, no prueba independiente nueva. La comparación contrasta candidatos concretos; no demuestra superioridad universal de un protocolo.

## Selección, características y balanceo

Variar un hiperparámetro por vez respecto de su referencia, sin producto cartesiano ni duplicados. Acotar la búsqueda a dos cambios individuales por algoritmo: RF (`max_depth=16`, `min_samples_leaf=10`) y XGBoost (`max_depth=2`, `reg_lambda=5`), en ambos protocolos y con/sin pesos. Logística permanece como referencia, sin búsqueda de C. Es una exploración acotada por costo, no una búsqueda exhaustiva. Después contrastar representaciones, contexto temporal y balanceo. Elegir por F1 macro promedio de validación; desempates por dispersión, tiempo y nombre. Conservar el mejor RF y XGBoost base para importancia por permutación; historia y balanceo parten de un único ganador base por protocolo.

Contexto temporal: señales pasadas del mismo paciente y segmento continuo, nunca etiquetas anteriores ni señales futuras. Una discontinuidad reinicia la historia; falta de antecedentes conserva NaN e indicador. La mediana se aprende dentro del entrenamiento. Al mezclar epochs, los retardos pueden compartir señales entre folds aunque sean causales.

Escalado, imputación, pesos y SMOTE se ajustan exclusivamente con entrenamiento. SMOTE se estudia sin historia ni pesos adicionales; validación y métricas de entrenamiento se calculan sobre observaciones reales. Reglas de balanceo en [ADR 0009](0009-distribuciones-y-desbalance-de-etapas.md).

## Diagnóstico y comparación de test reservado

Guardar una predicción y probabilidades OOF por epoch, configuración y protocolo. Distinguir promedio entre folds de métricas acumuladas. Informar F1 macro, precisión/recuperación/F1 por etapa, matrices, ROC-AUC y resultados por paciente con cobertura de etapas. Retirar Precision–Recall/AP de los diagnósticos activos; las salidas históricas quedan preservadas.

El test interno tuvo exposición en EDA y comparaciones previas: declarar esta limitación. Su evaluación histórica conserva código y resultados, sin reentrenar ni inferir allí. No transferir sus métricas a candidatos nuevos. La nueva comparación se guarda por separado sin sobrescribir artefactos históricos.

La comparación vigente utiliza los 16 pacientes del test reservado, no pacientes adicionales. Ambos candidatos se congelan tras desarrollo, se entrenan con los mismos 60 pacientes y se evalúan sobre los mismos 11.839 epochs. La reserva no interviene en selección y no se reajusta tras esta comparación. Su exposición histórica impide presentarla como evaluación independiente nueva. La evaluación externa queda únicamente como alternativa futura.

Conservar configuración, columnas, representación, retardos, balanceo, versiones y fuentes. Guardar pipelines y comprobar serialización con desarrollo antes de abrir resultados. Persistir probabilidades y clases una vez por candidato antes de calcular métricas desde archivos. El estado de una comparación incompleta bloquea reintentos; una completa verifica huellas y se relee sin entrenar ni inferir. Las salidas de revisión están separadas de las históricas.

## Interpretación del candidato final

Se conservan las importancias base y se añade XGBoost congelado con historia 1+2 minutos, 68 entradas. Se reentrena únicamente en cinco folds por pacientes de desarrollo, con medianas/pesos de entrenamiento, y se permuta solo validación. Se calculan cinco repeticiones por entrada y por grupo; primero promedio por fold y después media/desviación entre folds.

Los grupos son señales actuales, antecedentes de 1 minuto, antecedentes de 2 minutos e indicadores de disponibilidad. Dentro de cada grupo se usa una única permutación conjunta de filas para conservar relaciones entre sus columnas. Su importancia no es suma de las individuales, no mide causalidad y depende de correlaciones. No se seleccionan características ni se reajusta el modelo después del test. Se recuperan ejemplos históricos de parámetros únicamente con propósito explicativo, distinguiéndolos de nuevas ejecuciones.


## Alternativas y consecuencias

Una división única por paciente es más económica, pero depende más de las personas asignadas. GroupKFold mantiene grupos sin intentar conservar proporciones. StratifiedGroupKFold intenta distribuir etapas sin garantizar cobertura; comprobarla antes de entrenar. Estratificar no balancea clases.

La evaluación cronológica respondía al uso de pasado etiquetado para predecir períodos futuros del mismo paciente. Se retiró del alcance activo por decisión del equipo, conservando sus versiones anteriores en Git. Los retardos de señales siguen disponibles y no implican realizar ese protocolo de evaluación.

La selección sobre muchos candidatos puede optimizar en exceso los mismos folds; las diferencias pequeñas no prueban superioridad concluyente. La comparación sobre el test histórico amplía la evidencia descriptiva y debe reportar ambos resultados, incluso si el candidato seleccionado con epochs mezclados no mantiene su ventaja de validación.

## Alcance

La consigna ubica selección de técnicas, parámetros, evaluación e interpretación en la tercera entrega. La revisión mantiene únicamente wearable + PSG. El detalle operativo y los resultados efectivamente ejecutados viven en la documentación de la entrega; el ADR conserva las reglas y sus motivos.
