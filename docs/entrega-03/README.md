# Entrega 3 · Modelado y evaluación

## Estado y alcance

La [copia de revisión](../../temporal_version_tp_entrega03_revision.ipynb) contiene las salidas de Kaggle **hasta 4.5.2; la ejecución desde 4.5.3 está pendiente**. El [notebook oficial previo](../../temporal_version_tp_entrega03.ipynb) queda intacto para que el equipo compare ambos antes de consolidar la revisión.

Se clasifica el epoch actual de 30 segundos con wearable + PSG. Se seleccionará un candidato con pacientes separados y otro con epochs mezclados, usando el mismo catálogo de alternativas sobre 45.011 epochs de 60 pacientes. Los 16 pacientes ya evaluados históricamente quedan fuera de los nuevos ajustes.

Las salidas incorporadas corresponden a 16 configuraciones nuevas de hiperparámetros de RF/XGBoost, con y sin pesos y en ambos protocolos; logística queda como referencia sin ajustar C. Se ejecutaron con `N_JOBS=2`. Se conserva `N_JOBS=-1` para futuras ejecuciones, según lo acordado: los tiempos guardados pertenecen a la ejecución con dos núcleos. En 4.5.1 se conservaron exactamente las tablas finales de Kaggle: comparación general, sobreajuste, tiempos, F1 por etapa e interpretación de los cambios. Se muestran hasta tres configuraciones por algoritmo. El código muestra solo nombres durante las pruebas y el resumen completo al finalizar, sin las cuatro tablas detalladas de cada configuración. No se reentrenaron modelos ni se recalcularon cifras al incorporar estas salidas.

La ejecución de representaciones comparó la candidata con canales separados, manteniendo `log1p`. No hay resultados nuevos desde 4.5.3. Las exportaciones locales previas de `output/modelado_revision/` son parciales y no equivalen a esta ejecución de Kaggle.

## Cómo ejecutar la revisión

1. Subir el notebook de revisión a Kaggle con los CSV `dataset_epochs_v1.csv` y `dataset_modelado_candidato.csv` de la misma ejecución del ETL. No hace falta repetir el ETL crudo.
2. Ejecutar 4.1–4.6 desde un kernel limpio. Los resultados nuevos se guardan en `/kaggle/working/modelado_revision/`. `N_JOBS=-1` permite usar los núcleos de CPU disponibles para RF/XGBoost, como en el original; el código utiliza CPU.
3. La sección 4.7 tiene preparación/evaluación común y resultados/comparación. Requiere los dos CSV de pacientes adicionales, compatibles con el ETL y de personas distintas de la cohorte histórica. Sin rutas, informa que la comparación está pendiente. No sustituirlos por los 16 pacientes ya consultados.
4. No ejecutar 4.8: conserva el código y las salidas históricas del notebook original como referencia posterior a la comparación adicional. Son pacientes distintos: no es una comparación directa sobre los mismos casos. Las etiquetas `skip-execution` sirven para ejecución programática y pueden no ser respetadas por Kaggle; seleccionar los bloques activos en lugar de «ejecutar todo».
5. Compartir el `.ipynb` ejecutado y las exportaciones para interpretar resultados y actualizar únicamente los documentos afectados.

Se retiraron la evaluación cronológica, la propuesta solo wearable y Precision–Recall/AP de los diagnósticos activos. Se conservan historia causal por paciente, matrices, ROC-AUC y resultados por paciente. Las métricas mezcladas no demuestran, por sí solas, generalización a personas nuevas.

## Evaluación histórica protegida

El bloque histórico corresponde al XGBoost con pesos e historia 1+2 minutos, 68 entradas. Sus salidas guardadas muestran F1 macro 0,5412 y exactitud 0,6126 sobre los 16 pacientes. No transferir ese resultado a candidatos nuevos ni reutilizar el test para ajustes. Tuvo exposición histórica en EDA y comparaciones anteriores.

Las salidas del notebook se conservan exactamente. Los artefactos originales de `output/modelado/` no están disponibles en este checkout; la revisión no los reconstruye ni los sobrescribe. Las nuevas exportaciones están separadas.

## Documentación y verificaciones

El [resumen](resumen-notebook.md) describe la copia de revisión. El [informe](informe-modelado.md) y la [guía de experimentos](experimentos-hiperparametros.md) conservan resultados del notebook oficial previo y se actualizarán con la ejecución completa; no son resultados de la revisión. El [ADR metodológico](../adr/0011-modelado-posterior-a-la-entrega-etl.md) refleja las decisiones aprobadas.

La revisión conserva la huella del notebook de origen en sus metadatos. Se verificó estáticamente la sintaxis, los retiros acordados y la igualdad del código/salidas históricos. Las pruebas de integración de `tests/test_revision_entrega03.py` están preparadas; su verificación final requiere ejecución en un entorno de modelado y no se realizó tras los últimos cambios. No es necesario ejecutar entrenamientos en el Mac para editar el notebook.
