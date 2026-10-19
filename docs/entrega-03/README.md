# Entrega 3 · Modelado y evaluación

## Objetivo y estado

Clasificar un epoch de 30 segundos en W, N1, N2, N3 o REM. [Notebook autónomo](../../temporal_version_tp_entrega03.ipynb): ambos CSV existentes, sin ejecutar EDA/ETL. Predictores wearable + PSG; identidad, tiempo y etiqueta fuera de X. Los experimentos temporales usan señales pasadas, nunca etiquetas anteriores.

Dos escenarios de selección, sin consultar el test. Desarrollo: 45.011 epochs de 60 pacientes; reserva: 11.839 epochs de 16 pacientes. El protocolo por pacientes evalúa todos los epochs de desarrollo. El cronológico evalúa 37.490 epochs; excluye de validación los 7.521 del bloque inicial, conservados para entrenamiento. Cinco folds por escenario; gap cronológico de 15 minutos.

Se ejecutaron 147 comparaciones documentadas: Hiperparámetro: 84, Protocolo: 14, Contexto temporal: 14, Pesos: 9, SMOTE: 8, Representación: 8, Balanceo control: 6, Control: 4. Las referencias de epochs mezclados se conservan como diagnóstico. Las cifras son de desarrollo, no de prueba final.

Lectura recomendada: [resumen del notebook y trabajo pendiente](resumen-notebook.md), [informe para decisiones y exposición](informe-modelado.md), [guía detallada de experimentos](experimentos-hiperparametros.md).

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

## Selección de desarrollo

| Escenario | Candidato | F1 base | F1 candidato | Desviación | Exactitud | Brecha | Entrenamiento 5 folds (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Personas nuevas | contexto_pacientes_XGB_lag_1+2 | 0.4907 | 0.5053 | 0.0265 | 0.6043 | 0.3010 | 42.0055 |
| Pacientes conocidos: lecturas futuras | contexto_temporal_XGB_lag_1+2 | 0.5567 | 0.5803 | 0.0698 | 0.7050 | 0.3784 | 45.3840 |

Las configuraciones exactas y conclusiones de desarrollo están en el [informe](informe-modelado.md). La selección para personas nuevas quedó congelada y se evaluó posteriormente; el candidato cronológico sigue pendiente de una prueba independiente. Las cifras de esta tabla siguen siendo de validación.

## Flujo del notebook

1. **4.1:** validar CSV, claves, alineación, entradas finitas y cinco etapas; reutilizar reserva por pacientes y huellas SHA256. Guardar folds y cobertura completa en CSV; mostrar tablas pequeñas de pacientes.
2. **4.2–4.4:** referencias Dummy, logística, RF y XGB, con/sin pesos; tres protocolos. Cada configuración muestra folds, promedio/desviación, brecha y métricas por etapa. Resúmenes separados por protocolo.
3. **4.5.1–4.5.2:** mismo catálogo de hiperparámetros y representaciones para los dos escenarios de selección. Variaciones individuales; luego ablaciones de log1p/canales.
4. **4.5.3:** retardos de señales sobre el ganador base de cada escenario; continuidad de 30 s, reinicio ante huecos, indicadores e imputación por fold.
5. **4.5.4:** controles sin pesos, con pesos y escalado; SMOTE k=3/5, objetivos por clase 50/100 %. Solo entrenamiento, métricas sobre observaciones reales.
6. **4.5.5:** discusión breve y candidatos independientes por escenario. Cada comparación tiene conclusión en la guía.
7. **4.6.1–4.6.5:** importancia por permutación; errores/matrices; PR/AP; ROC/AUC; pacientes, en apartados separados. Importancia de RF/XGB sin historia/SMOTE, diagnósticos restantes del candidato elegido por escenario.
8. **4.7:** solo wearable pendiente. **4.8:** ejecución independiente, configuración congelada y test evaluado una vez para personas nuevas; relectura sin entrenamiento/inferencia. **4.9:** conserva el cierre de desarrollo y añade las conclusiones finales.

## Evaluación final ejecutada · personas nuevas

Se congeló `contexto_pacientes_XGB_lag_1+2`: 200 rondas, profundidad 4, tasa 0,1, lambda 5, muestreos 0,8, semilla 42, pesos balanceados e historia 1+2 minutos; 68 columnas, imputación de desarrollo, sin escalado ni SMOTE. Se entrenó con los 60 pacientes de desarrollo.

| Evaluación | F1 macro | Exactitud |
| --- | --- | --- |
| Validación por pacientes: media de cinco folds | 0.5053 | 0.6043 |
| Test: agregado de 16 personas nuevas | 0.5412 | 0.6126 |

El test obtuvo F1 macro **0.5412** y exactitud **0.6126** en 11.839 epochs de 16 pacientes. La diferencia frente a la media de validación es +0.0358. La cifra global mayor no prueba superioridad ni estabilidad universal: cambian las personas, la distribución y la cantidad de datos usada para entrenar. No se reajustaron parámetros, señales ni umbrales con este resultado.

**N1 sigue siendo la principal debilidad:** precisión 0.1733, recuperación 0.2958, F1 0.2185, AP 0.1699. Aproximadamente el 82.7 % de las detecciones N1 son falsas y se omite una proporción importante de sus casos reales. El resultado no justifica afirmar buen reconocimiento de todas las etapas.

F1 por paciente, usando cinco clases fijas: mínimo 0.1913, máximo 0.6369. 11 de los 16 pacientes no tienen las cinco etapas observadas; esa cobertura limita comparaciones individuales. La heterogeneidad y los errores de N1 siguen siendo límites relevantes.

Artefactos: [pipeline con imputador](../../output/modelado/test_final/pipeline.joblib), [configuración congelada](../../output/modelado/configuracion_congelada.json), [predicciones únicas](../../output/modelado/predicciones_test.csv), [métricas](../../output/modelado/metricas_test.json). `modelo.ubj` respalda XGBoost; para inferencia usar el pipeline completo y las mismas reglas de historia/columnas.

`AUTORIZAR_APERTURA_TEST_FINAL=False` queda como valor seguro. Con resultados completos, 4.8 verifica huellas y los muestra sin entrenar ni predecir. Una apertura incompleta se detiene sin reintento automático. No borrar `test_abierto.json`; al trasladar el notebook copiar también la configuración, el marcador y los artefactos de `output/modelado/`.

## Qué mirar

- F1 macro: media del F1 de cinco etapas, con igual peso; `F1 = 2PR/(P+R)`. Media entre folds y métrica OOF acumulada son distintas.
- Precisión: proporción de detecciones correctas; recuperación: proporción de casos reales detectados; soporte: cantidad real. Revisar las cinco etapas, especialmente N1.
- Exactitud: proporción total de aciertos, sensible al predominio de N2. No reemplaza F1 macro.
- Brecha: F1 entrenamiento menos validación. Reducirla sin mejorar validación no alcanza. Desviación entre folds no es prueba estadística de superioridad.
- PR: recuperación en X, precisión en Y; referencia de prevalencia y resumen AP. Argmax muestra la decisión multiclase. ROC-AUC complementa, no reemplaza PR.
- Pacientes: cinco clases fijas y cobertura informada; registros largos pesan más en agregados por epoch.

Pesos por observación: `N_train / (5 * N_clase_train)`, recalculados por fold. SMOTE no combina pesos; mantiene validación/test originales. [ADR 0009](../adr/0009-distribuciones-y-desbalance-de-etapas.md).

## Ejecución, salidas y verificación

Las secciones 4.1–4.7 conservan los experimentos ejecutados. Para consultar la evaluación final, reiniciar el kernel y ejecutar **solo 4.8**, desde su primera celda. Requiere numpy, pandas, scikit-learn, matplotlib, IPython, xgboost y joblib; imbalanced-learn corresponde a las pruebas previas. Local: CSV en `etl_v1/`, dependencias opcionales en `output/modelado-deps`. Kaggle: una coincidencia por CSV bajo `/kaggle/input`. El notebook no instala paquetes automáticamente.

Salidas en `output/modelado/` o `/kaggle/working/modelado/`: asignación de pacientes, folds/elegibilidad, cobertura, versiones, configuraciones, métricas, OOF, pesos, cantidades sintéticas, cobertura de historia, conclusiones, importancia y figuras. Reutilizar asignación con mismas fuentes/semilla; no cambiar pacientes para mejorar métricas.

Los experimentos de desarrollo ya se habían ejecutado desde un kernel limpio; sus tablas de discusión se compactaron desde los registros obtenidos. En esta etapa se entrenó únicamente el candidato congelado, conservando las métricas, figuras y salidas anteriores.

Diecinueve pruebas de integración verifican experimentos y flujo final: equivalencia de historia, causalidad/huecos/pacientes, imputación/pesos solo de desarrollo, serialización, inferencia única, bloqueo de aperturas incompletas, integridad y relectura sin entrenamiento. Se ejecutó todo 4.8 primero en un kernel limpio con datos sintéticos. Tras la evaluación real, otra sesión ejecutó 4.8 con entrenamiento e inferencia bloqueados y sin modificar los artefactos.

Las huellas canónicas de las celdas 0–32 (código, salidas y explicaciones de 4.1–4.6), el texto de 4.7 y todas las exportaciones `metricas.csv` anteriores coinciden con las registradas antes de editar. No se volvió a ejecutar la búsqueda ni se reemplazaron sus resultados.

Notebook `temporal_version_tp_entrega03_ANTERIOR.ipynb` intacto: SHA256 `e4757dab640cd660ae9bd5dfb5f871df5a7fd57ff5f413e235b21c5669d6a42a`.

## Límites y pendientes

El test interno tuvo exposición histórica en EDA y comparaciones de la cohorte completa; no presentarlo como históricamente intacto. Ya fue evaluado: no usarlo para reajustar. El test por personas nuevas no reemplaza una prueba temporal independiente de pacientes conocidos ni la evaluación externa con personas adicionales.

Pendientes: prueba temporal independiente para pacientes conocidos, evaluación externa y solo wearable. Combinaciones de hiperparámetros o SMOTE+historia serían otra ronda de desarrollo, con evaluación independiente propia; no nuevas optimizaciones sobre este test.

Decisiones compartidas: [ADR 0007](../adr/0007-revision-y-seleccion-de-caracteristicas.md), [ADR 0011](../adr/0011-modelado-posterior-a-la-entrega-etl.md); [entrega 2](../entrega-02/README.md).
