# Entrega 3 · Modelado y evaluación

## Objetivo y estado

Clasificar un epoch de 30 segundos en W, N1, N2, N3 o REM. [Notebook autónomo](../../temporal_version_tp_entrega03.ipynb): ambos CSV existentes, sin ejecutar EDA/ETL. Predictores wearable + PSG; identidad, tiempo y etiqueta fuera de X. Los experimentos temporales usan señales pasadas, nunca etiquetas anteriores.

Dos escenarios de selección, sin consultar el test. Desarrollo: 45.011 epochs de 60 pacientes; reserva: 11.839 epochs de 16 pacientes. El protocolo por pacientes evalúa todos los epochs de desarrollo. El cronológico evalúa 37.490 epochs; excluye de validación los 7.521 del bloque inicial, conservados para entrenamiento. Cinco folds por escenario; gap cronológico de 15 minutos.

Se ejecutaron 147 comparaciones documentadas: Hiperparámetro: 84, Protocolo: 14, Contexto temporal: 14, Pesos: 9, SMOTE: 8, Representación: 8, Balanceo control: 6, Control: 4. Las referencias de epochs mezclados se conservan como diagnóstico. Las cifras son de desarrollo, no de prueba final.

Lectura recomendada: [informe para decisiones y exposición](informe-modelado.md), [guía detallada de experimentos](experimentos-hiperparametros.md).

## Referencia anterior preservada



[Referencia original](referencia-previa.json): código, contadores y salidas anteriores, con métricas por fold/etapa, parámetros y tiempos. Cinco folds por paciente sobre 56.850 epochs de 76 pacientes, sin test interno. No se recuperaron objetos entrenados ni probabilidades OOF que solo existían en memoria.

| Configuración | F1 macro promedio ± DE | Exactitud | Entrenamiento total (s) |
| --- | --- | --- | --- |
| RF sin pesos | 0,4597 ± 0,0616 | 0,6612 | 138,7891 |
| RF con pesos | 0,4370 ± 0,0489 | 0,6545 | 129,0336 |
| XGBoost sin pesos | 0,4641 ± 0,0470 | 0,6483 | 16,6874 |
| XGBoost con pesos | 0,4923 ± 0,0217 | 0,5921 | 16,6625 |

Son salidas guardadas, no cifras recalculadas. Las nuevas comparaciones usan desarrollo reducido y no equivalen a repetir aquella evaluación. XGB ponderado lideraba por F1 macro; RF sin pesos por exactitud.

## Comparación ejecutada de protocolos

| Modelo | Pesos | Pacientes separados | Epochs mezclados | Cronológico |
| --- | --- | --- | --- | --- |
| RF | No | 0.3847 ± 0.0284 | 0.7617 ± 0.0083 | 0.4822 ± 0.0591 |
| RF | Sí | 0.4412 ± 0.0288 | 0.7860 ± 0.0081 | 0.5424 ± 0.0681 |
| XGB | No | 0.4465 ± 0.0322 | 0.7418 ± 0.0077 | 0.5133 ± 0.0604 |
| XGB | Sí | 0.4859 ± 0.0299 | 0.7273 ± 0.0052 | 0.5452 ± 0.0448 |

La mezcla aleatoria comparte pacientes y observaciones próximas. El cronológico predice el futuro con pasado disponible; pacientes separados evalúa personas desconocidas. No elegir el protocolo por la mayor cifra ni promediar los escenarios.

## Candidatos provisionales

| Escenario | Candidato | F1 base | F1 candidato | Desviación | Exactitud | Brecha | Entrenamiento 5 folds (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Personas nuevas | contexto_pacientes_XGB_lag_1+2 | 0.4907 | 0.5053 | 0.0265 | 0.6043 | 0.3010 | 42.0055 |
| Pacientes conocidos: lecturas futuras | contexto_temporal_XGB_lag_1+2 | 0.5567 | 0.5803 | 0.0698 | 0.7050 | 0.3784 | 45.3840 |

Las configuraciones exactas, debilidades y conclusiones temporales/SMOTE están en el [informe](informe-modelado.md). La mayor media no demuestra una diferencia concluyente. La validación orientó selección entre muchas pruebas; el test continúa cerrado.

## Flujo del notebook

1. **4.1:** validar CSV, claves, alineación, entradas finitas y cinco etapas; reutilizar reserva por pacientes y huellas SHA256. Guardar folds y cobertura completa en CSV; mostrar tablas pequeñas de pacientes.
2. **4.2–4.4:** referencias Dummy, logística, RF y XGB, con/sin pesos; tres protocolos. Cada configuración muestra folds, promedio/desviación, brecha y métricas por etapa. Resúmenes separados por protocolo.
3. **4.5.1–4.5.2:** mismo catálogo de hiperparámetros y representaciones para los dos escenarios de selección. Variaciones individuales; luego ablaciones de log1p/canales.
4. **4.5.3:** retardos de señales sobre el ganador base de cada escenario; continuidad de 30 s, reinicio ante huecos, indicadores e imputación por fold.
5. **4.5.4:** controles sin pesos, con pesos y escalado; SMOTE k=3/5, objetivos por clase 50/100 %. Solo entrenamiento, métricas sobre observaciones reales.
6. **4.5.5:** discusión breve y candidatos independientes por escenario. Cada comparación tiene conclusión en la guía.
7. **4.6.1–4.6.5:** importancia por permutación; errores/matrices; PR/AP; ROC/AUC; pacientes, en apartados separados. Importancia de RF/XGB sin historia/SMOTE, diagnósticos restantes del candidato elegido por escenario.
8. **4.7:** solo wearable pendiente. **4.8:** congelación y test desactivados. El test actual sirve para personas nuevas. **4.9:** conclusiones y límites.

## Qué mirar

- F1 macro: media del F1 de cinco etapas, con igual peso; `F1 = 2PR/(P+R)`. Media entre folds y métrica OOF acumulada son distintas.
- Precisión: proporción de detecciones correctas; recuperación: proporción de casos reales detectados; soporte: cantidad real. Revisar las cinco etapas, especialmente N1.
- Exactitud: proporción total de aciertos, sensible al predominio de N2. No reemplaza F1 macro.
- Brecha: F1 entrenamiento menos validación. Reducirla sin mejorar validación no alcanza. Desviación entre folds no es prueba estadística de superioridad.
- PR: recuperación en X, precisión en Y; referencia de prevalencia y resumen AP. Argmax muestra la decisión multiclase. ROC-AUC complementa, no reemplaza PR.
- Pacientes: cinco clases fijas y cobertura informada; registros largos pesan más en agregados por epoch.

Pesos por observación: `N_train / (5 * N_clase_train)`, recalculados por fold. SMOTE no combina pesos; mantiene validación/test originales. [ADR 0009](../adr/0009-distribuciones-y-desbalance-de-etapas.md).

## Ejecución, salidas y verificación

Ejecutar todo desde un kernel limpio con numpy, pandas, scikit-learn, matplotlib, IPython, xgboost e imbalanced-learn. Local: CSV en `etl_v1/`; dependencias opcionales en `output/modelado-deps`. Kaggle: una coincidencia por CSV bajo `/kaggle/input`. El notebook no instala paquetes automáticamente. Versiones registradas en cada ejecución.

Salidas en `output/modelado/` o `/kaggle/working/modelado/`: asignación de pacientes, folds/elegibilidad, cobertura, versiones, configuraciones, métricas, OOF, pesos, cantidades sintéticas, cobertura de historia, conclusiones, importancia y figuras. Reutilizar asignación con mismas fuentes/semilla; no cambiar pacientes para mejorar métricas.

Se ejecutó el entrenamiento completo desde un kernel limpio. Las tablas de discusión se compactaron después desde los registros ejecutados, conservando métricas, figuras y salidas de entrenamiento.

Trece pruebas de integración verifican controles originales y nuevos: causalidad/huecos/pacientes en historia, cronología/gap/OOF elegibles, imputación exclusiva de entrenamiento, SMOTE solo en entrenamiento y soporte real, compatibilidad de XGBoost con el pipeline de muestreo, test sintético de apertura única y tablas HTML completas. El test sintético no accede al test real.

Notebook `temporal_version_tp_entrega03_ANTERIOR.ipynb` intacto: SHA256 `e4757dab640cd660ae9bd5dfb5f871df5a7fd57ff5f413e235b21c5669d6a42a`.

## Límites y pendientes

El test interno tuvo exposición histórica en EDA y comparaciones de la cohorte completa; declarar esta limitación. Mantener `EJECUTAR_TEST_FINAL=False` hasta congelar modelo, entradas y preprocesamiento; no reajustar con test. El test por personas nuevas no reemplaza una prueba futura independiente de pacientes conocidos. Pacientes adicionales permitirán evaluación externa.

Pendientes: solo wearable, combinaciones simultáneas de hiperparámetros, SMOTE+historia, congelación y evaluación final. El informe no presenta estos puntos como ejecutados.

Decisiones compartidas: [ADR 0007](../adr/0007-revision-y-seleccion-de-caracteristicas.md), [ADR 0011](../adr/0011-modelado-posterior-a-la-entrega-etl.md); [entrega 2](../entrega-02/README.md).
