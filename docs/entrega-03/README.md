# Entrega 3 · Modelado y evaluación

## Estado y resultado

La [revisión](../../temporal_version_tp_entrega03_revision.ipynb) tiene ejecutadas las secciones activas **4.1–4.7**: selección, historia, SMOTE, diagnósticos y comparación sobre los mismos **16 pacientes de test reservado**. No requiere pacientes adicionales. El [notebook oficial](../../temporal_version_tp_entrega03.ipynb) y su evaluación histórica se conservan.

Desarrollo: 45.011 epochs / 60 pacientes; test: 11.839 epochs / 16 personas distintas. Se seleccionó un candidato por protocolo usando el mismo catálogo acotado y sus cinco folds. La búsqueda no determina hiperparámetros óptimos.

| Selección | Algoritmo | Pesos | Historia (min) | Entradas | F1 validación ± DE | F1 test | Exactitud test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pacientes separados | XGB | Sí | [1, 2] | 68 | 0,5053 ± 0,0265 | 0,5412 | 0,6126 |
| Epochs mezclados | RF | No | Sin historia | 22 | 0,8006 ± 0,0038 | 0,4985 | 0,6278 |

En los mismos 16 pacientes, el candidato seleccionado mediante **pacientes separados** obtuvo el mayor F1 macro. Diferencia epochs menos pacientes: **-0,0426**. Las validaciones no se comparan como si midieran generalización equivalente. La diferencia en test corresponde a estos candidatos concretos; pueden cambiar algoritmo, entradas y parámetros además del protocolo. No se realizaron reajustes posteriores.

## Qué se probó

- Referencias Dummy, logística, RF y XGBoost con/sin pesos.
- 16 variantes individuales: RF profundidad 16 o mínimo por hoja 10; XGBoost profundidad 2 o lambda 5, con/sin pesos en ambos protocolos. No se amplió el catálogo ni se ajustó C de logística.
- Representación candidata frente a canales separados, ambas con `log1p`.
- Historia de 1/2/5/10/15 minutos, 5+10 y los dos mejores individuales, sobre el ganador base de cada protocolo.
- Controles sin/con pesos y escalado; SMOTE vecinos 3/5 y objetivos 50/100 %, sin historia ni pesos adicionales.

Se documentaron 65 comparaciones contra referencia en esta ronda. [Resumen por sección](resumen-notebook.md), [informe para exponer](informe-modelado.md), [detalle y conclusión de cada prueba](experimentos-hiperparametros.md).

## Interpretación final completada

Se recuperaron seis pruebas históricas de parámetros para explicar regularización, capacidad y costo, sin ampliar búsquedas. Se calcularon las importancias de las 68 entradas del XGBoost final y de cuatro grupos sobre validación de desarrollo; los resultados se muestran en 4.6.1 y en el [informe](informe-modelado.md#interpretación-del-xgboost-final-con-historia).

La mayor caída media correspondió al grupo **actuales** (0,2306). Los antecedentes de un minuto y dos minutos tuvieron caídas medias 0,0476 y 0,0218; describen dependencia del modelo, no una mejora garantizada al agregarlos. Los indicadores de disponibilidad tuvieron caída media 0,0006. Las desviaciones reflejan variación entre folds; no constituyen una prueba estadística de superioridad entre grupos.

Para ejecutar únicamente esta interpretación en un kernel limpio, cargar las definiciones `agregar_historia`, `buscar_csv` y `mostrar_tabla` de 4.1 y ejecutar el nuevo bloque de 4.6.1 con los archivos congelados de revisión. No ejecutar búsquedas ni 4.7/4.8. La interpretación no modifica el modelo evaluado.


## Ejecución y conservación

El desarrollo nuevo se ejecutó desde un kernel limpio con `N_JOBS=-1`, CPU, semilla 42 y versiones registradas. No estaban disponibles las exportaciones completas de Kaggle de 4.1–4.5.2, por lo que se repitieron los bloques necesarios en vez de reconstruir predicciones desde tablas. Las salidas recibidas de Kaggle (`N_JOBS=2`) se conservaron como evidencia anterior; sus tiempos no son comparables directamente con esta ejecución. Los registros `ejecuciones.jsonl` distinguen entrenamiento ejecutado y reutilización compatible.

Antes de predecir el test, la comprobación binaria de serialización de RF detectó diferencias de redondeo de aproximadamente 3,3 × 10⁻¹⁶, sin cambiar clases. Se corrigió el control a tolerancia 10⁻¹² con clases idénticas y se agregó una prueba de regresión. Se conservó el estado interrumpido y se completó 4.7 en otro kernel limpio desde los dos pipelines guardados y verificados, sin reentrenarlos ni repetir predicciones de test. La continuación preapertura quedó auditada; el flujo normal sigue bloqueando estados incompletos. Los tiempos exactos de ese entrenamiento final no se habían persistido antes de la interrupción y se muestran ausentes, sin estimarlos. Sí están disponibles los costos de entrenamiento de validación y los tiempos reales de inferencia.

Las nuevas salidas viven en `output/modelado_revision/`. Los artefactos de comparación están en `comparacion_test/`: configuraciones congeladas, pipelines, pruebas de serialización, predicciones únicas, métricas, diagnósticos y diferencias por paciente. El notebook oficial y el código/salidas históricos de 4.8 se preservaron. No se ejecutó 4.8.

Para consultar 4.7 con resultados completos, conservar todos sus artefactos y `AUTORIZAR_COMPARACION_TEST=False`: se releen sin entrenar ni inferir. Una apertura incompleta se bloquea y no debe reiniciarse automáticamente. Las configuraciones y columnas deben coincidir. No borrar `comparacion_test/estado.json`.

No ejecutar las celdas de 4.8: sus salidas corresponden al modelo histórico, F1 macro 0,5412 y exactitud 0,6126. Son los mismos 16 pacientes con otra selección y entorno; no transferir esas cifras a los candidatos actuales. Los marcadores `skip-execution` pueden no ser respetados por «ejecutar todo» en Kaggle.

## Límites y verificación

El test ya había sido consultado y tuvo exposición histórica en EDA/comparaciones de la cohorte completa. Esta es una comparación posterior sobre personas excluidas de los nuevos entrenamientos, **no una nueva prueba independiente**. No se usó para seleccionar ni reajustar los candidatos de esta ronda. La selección entre muchas pruebas puede optimizar en exceso la validación.

Al mezclar epochs se comparten personas y observaciones próximas. Con historia, un antecedente puede contener señales de otro fold; no contiene su etiqueta, pero la dependencia puede favorecer las métricas. Las etapas ausentes y las distintas duraciones limitan comparaciones individuales. Los modelos utilizan wearable + PSG; no demuestran rendimiento solo wearable.

Se ejecutaron 29 pruebas sintéticas e integración del flujo revisado (22 existentes y siete de interpretación): historia, faltantes, pesos/SMOTE exclusivos de entrenamiento, serialización, una inferencia de test por candidato, relectura e integridad. La aceptación real verifica OOF, claves, probabilidades y conservación de artefactos anteriores. Las verificaciones disponibles se registran en `output/verificacion/aceptacion_revision_test.json`. El archivo `ANTERIOR` no estaba disponible en este checkout: no se pudo verificar su huella en esta ronda; sí las del notebook oficial y los artefactos históricos disponibles.

Una evaluación externa con personas adicionales sería una ampliación futura, no un requisito para ejecutar esta comparación. No quedan entrenamientos pendientes dentro de esta ronda, incluida la importancia final con historia. [Decisión metodológica](../adr/0011-modelado-posterior-a-la-entrega-etl.md).
