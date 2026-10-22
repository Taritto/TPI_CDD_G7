# Experimentos de hiperparámetros, historia y balanceo

## Ronda vigente · revisión ejecutada

Selección por pacientes separados y epochs mezclados con el mismo catálogo reducido. Las fuentes, folds, versiones y configuraciones exactas están en las exportaciones del [notebook de revisión](../../temporal_version_tp_entrega03_revision.ipynb). No se amplió la búsqueda: 16 variantes individuales de RF/XGBoost; logística conserva C=1. Los valores son alternativas ensayadas, no óptimos demostrados.

El desarrollo nuevo se ejecutó desde un kernel limpio con `N_JOBS=-1`, CPU, semilla 42 y versiones registradas. No estaban disponibles las exportaciones completas de Kaggle de 4.1–4.5.2, por lo que se repitieron los bloques necesarios en vez de reconstruir predicciones desde tablas. Las salidas recibidas de Kaggle (`N_JOBS=2`) se conservaron como evidencia anterior; sus tiempos no son comparables directamente con esta ejecución. Los registros `ejecuciones.jsonl` distinguen entrenamiento ejecutado y reutilización compatible.

Antes de predecir el test, la comprobación binaria de serialización de RF detectó diferencias de redondeo de aproximadamente 3,3 × 10⁻¹⁶, sin cambiar clases. Se corrigió el control a tolerancia 10⁻¹² con clases idénticas y se agregó una prueba de regresión. Se conservó el estado interrumpido y se completó 4.7 en otro kernel limpio desde los dos pipelines guardados y verificados, sin reentrenarlos ni repetir predicciones de test. La continuación preapertura quedó auditada; el flujo normal sigue bloqueando estados incompletos. Los tiempos exactos de ese entrenamiento final no se habían persistido antes de la interrupción y se muestran ausentes, sin estimarlos. Sí están disponibles los costos de entrenamiento de validación y los tiempos reales de inferencia.

Las nuevas salidas viven en `output/modelado_revision/`. Los artefactos de comparación están en `comparacion_test/`: configuraciones congeladas, pipelines, pruebas de serialización, predicciones únicas, métricas, diagnósticos y diferencias por paciente. El notebook oficial y el código/salidas históricos de 4.8 se preservaron. No se ejecutó 4.8.

### Candidatos fijados antes de comparar test

- **Pacientes separados:** `contexto_pacientes_XGB_lag_1+2`; `n_estimators=200`, `max_depth=4`, `learning_rate=0.1`, `reg_lambda=5`, `min_child_weight=None`, `subsample=0.8`, `colsample_bytree=0.8`; representación `candidata`; pesos balanceados; retardos [1, 2]; SMOTE `None`; 68 entradas. Las opciones predeterminadas se registran en la configuración congelada.
- **Epochs mezclados:** `smote_epochs_RF_ratio1.0_k5`; `n_estimators=200`, `max_depth=None`, `min_samples_leaf=2`, `max_features=sqrt`; representación `candidata`; pesos desactivados; retardos []; SMOTE `{'ratio': 1.0, 'k': 5}`; 22 entradas. Las opciones predeterminadas se registran en la configuración congelada.

| Selección | Algoritmo | Pesos | Historia (min) | Entradas | F1 validación ± DE | F1 test | Exactitud test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pacientes separados | XGB | Sí | [1, 2] | 68 | 0,5053 ± 0,0265 | 0,5412 | 0,6126 |
| Epochs mezclados | RF | No | Sin historia | 22 | 0,8006 ± 0,0038 | 0,4985 | 0,6278 |

### Pruebas históricas adicionales: efecto de los hiperparámetros

Resultados recuperados de exportaciones del notebook original, **sin nuevos entrenamientos ni búsqueda ampliada**.
Corresponden a pacientes separados, pesos balanceados y 22 variables sin historia. Se verificaron las mismas fuentes,
versiones y folds de desarrollo. No son pruebas sobre el XGBoost final de 68 entradas y no se incorporan retroactivamente
a la selección congelada. Los tiempos pertenecen a esa ejecución histórica, no se mezclan con los tiempos actuales.

| Cambio histórico | F1 referencia → prueba | Brecha referencia → prueba | Entrenamiento referencia → prueba (s) | Lectura breve |
| --- | --- | --- | --- | --- |
| XGB: lambda 1 → 5 | 0,4859 → 0,4907 | 0,2974 → 0,2879 | 16,3564 → 16,6298 | Pequeña mejora observada; mayor regularización no garantiza mejorar siempre. |
| XGB: profundidad 4 → 6 | 0,4859 → 0,4803 | 0,2974 → 0,4154 | 16,3564 → 30,6349 | Más capacidad aumentó la brecha y empeoró validación. |
| XGB: rondas 200 → 400 | 0,4859 → 0,4845 | 0,2974 → 0,3657 | 16,3564 → 35,4488 | Más costo sin mejora observada de validación. |
| XGB: tasa 0,1 → 0,03 | 0,4859 → 0,4659 | 0,2974 → 0,2064 | 16,3564 → 17,5536 | Con 200 rondas fijas empeoró; no prueba que una tasa menor sea siempre peor. |
| RF: mínimo por hoja 2 → 10 | 0,4412 → 0,4614 | 0,5190 → 0,3761 | 37,1971 → 11,2175 | Menos hojas específicas mejoró validación y redujo la brecha. |
| RF: mínimo por hoja 2 → 30 | 0,4412 → 0,4483 | 0,5190 → 0,2795 | 37,1971 → 6,7703 | Más restricción no conservó toda la mejora obtenida con 10. |

La brecha es F1 de entrenamiento menos validación. Menor brecha no basta si empeora la predicción.
Estas pruebas justifican decisiones dentro de las alternativas ensayadas; no demuestran hiperparámetros óptimos.
Detalle y procedencia por prueba en la [guía de experimentos](experimentos-hiperparametros.md).


### Interpretación del XGBoost final con historia

Se mantuvo la configuración congelada XGBoost ponderada con historia 1+2 minutos y sus 68 entradas. Se reentrenó exclusivamente en los cinco folds por pacientes de desarrollo, con imputación y pesos aprendidos en entrenamiento. Cinco permutaciones por variable y por grupo dentro de cada validación; primero se promedian repeticiones por fold y después los cinco folds con igual peso. El F1 base medio fue 0,5053, coherente con la selección ya guardada. No se ejecutó ni se volvió a predecir el test.

| Grupo permutado conjuntamente | Columnas | Caída media de F1 macro | Desviación entre folds |
| --- | --- | --- | --- |
| Actuales | 22 | 0,2306 | 0,0244 |
| Hace 1 minuto | 22 | 0,0476 | 0,0258 |
| Hace 2 minutos | 22 | 0,0218 | 0,0307 |
| Disponibilidad | 2 | 0,0006 | 0,0003 |

La mayor caída media correspondió al grupo **actuales** (0,2306). Los antecedentes de un minuto y dos minutos tuvieron caídas medias 0,0476 y 0,0218; describen dependencia del modelo, no una mejora garantizada al agregarlos. Los indicadores de disponibilidad tuvieron caída media 0,0006. Las desviaciones reflejan variación entre folds; no constituyen una prueba estadística de superioridad entre grupos.

Entradas individuales destacadas: `EOG_max_std`, `C4-M1_std`, `CHIN_std`, `F4-M1_std`, `CZ - T4_std`. El notebook muestra las 20 mayores caídas medias por color de grupo y exporta las 68. Primeras ocho:

| Entrada | Grupo | Caída media de F1 macro | Desviación entre folds |
| --- | --- | --- | --- |
| EOG_max_std | Actuales | 0,0353 | 0,0144 |
| C4-M1_std | Actuales | 0,0266 | 0,0243 |
| CHIN_std | Actuales | 0,0243 | 0,0223 |
| F4-M1_std | Actuales | 0,0216 | 0,0214 |
| CZ - T4_std | Actuales | 0,0188 | 0,0320 |
| T3 - CZ_std | Actuales | 0,0105 | 0,0133 |
| ACC_axes_std_norm_log1p | Actuales | 0,0083 | 0,0023 |
| O2-M1_std | Actuales | 0,0069 | 0,0058 |

La importancia conjunta se calcula permutando todas las columnas de un grupo con el mismo orden de filas y dejando las demás intactas. **No es la suma de importancias individuales ni un porcentaje causal**; los grupos tienen tamaños diferentes. La correlación puede repartir u ocultar información, y las permutaciones pueden generar combinaciones poco habituales. Una caída negativa no garantiza mejorar al quitar una entrada. Estos resultados no cambian columnas, parámetros ni candidatos.

Las exportaciones están en `output/modelado_revision/interpretacion_xgb_historia/`: permutaciones completas, medias por fold, tablas individuales/grupales, medianas y pesos de entrenamiento, métricas base, trazabilidad y dos gráficos. Una ejecución completa se verifica y relee sin entrenar; una incompleta se conserva y bloquea sobrescrituras.


### Historia y SMOTE: evidencia decisiva

| Protocolo | Prueba | Mejor variante observada | F1 referencia | F1 variante | Diferencia | Brecha | Entrenamiento 5 folds (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pacientes separados | Contexto temporal | Historia 1+2 minutos (dos mejores individuales) | 0,4907 | 0,5053 | 0,0147 | 0,3010 | 12,1839 |
| Pacientes separados | SMOTE | SMOTE objetivo 100% de mayoritaria; k=3 | 0,4451 | 0,4860 | 0,0409 | 0,2911 | 12,7084 |
| Epochs mezclados | Contexto temporal | Historia 15 minutos | 0,7860 | 0,7888 | 0,0029 | 0,1777 | 13,6455 |
| Epochs mezclados | SMOTE | SMOTE objetivo 100% de mayoritaria; k=5 | 0,7645 | 0,8006 | 0,0360 | 0,1947 | 38,1493 |

En la tabla, SMOTE se contrasta con el control escalado sin pesos. Comparación adicional frente al control ponderado sin historia:

- **Pacientes separados:** mejor SMOTE 0,4860; control ponderado sin historia 0,4491; diferencia SMOTE menos ponderado 0,0369.
- **Epochs mezclados:** mejor SMOTE 0,8006; control ponderado sin historia 0,7617; diferencia SMOTE menos ponderado 0,0388.

Historia y SMOTE se probaron por separado sobre el ganador base de cada protocolo. Los controles originales, ponderados y escalados permiten distinguir cambios de ponderación, escalado y remuestreo. No se crean pacientes nuevos; el test y las validaciones permanecen reales. Diferencias pequeñas no prueban superioridad concluyente; una brecha menor no compensa por sí sola menor F1 de validación.

### Detalle y conclusión de cada prueba ejecutada

Se registraron 65 comparaciones: Hiperparámetro: 16, Contexto temporal: 14, SMOTE: 8, Protocolo: 7, Balanceo control: 6, Pesos: 6, Control: 4, Representación: 4. Los tiempos son los observados en esta ejecución; las repeticiones compatibles conservan el tiempo de su entrenamiento original. Las diferencias de etapas se indican con respecto a la referencia del mismo experimento.

#### Pacientes separados

**Pesos**

- **`pacientes_Logistica_pesos1`** frente a `pacientes_Logistica_pesos0`: Sin pesos → pesos balanceados. F1 0,2610 → 0,3467 (Δ 0,0857); DE 0,0390; brecha 0,0729 (Δ 0,0354); entrenamiento 2,3343 s (Δ -0,5821 s). REM: ΔF1 +0.3323, Δprecisión +0.0723, Δrecuperación +0.6400; N2: ΔF1 -0.2359, Δprecisión +0.1961, Δrecuperación -0.5756. **Conclusión:** Mayor F1 promedio en 5/5 folds; la brecha no se redujo claramente. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`pacientes_RF_pesos1`** frente a `pacientes_RF_pesos0`: Sin pesos → pesos balanceados. F1 0,3847 → 0,4412 (Δ 0,0565); DE 0,0288; brecha 0,5190 (Δ -0,0857); entrenamiento 32,1851 s (Δ -9,6967 s). N3: ΔF1 +0.2340, Δprecisión -0.2604, Δrecuperación +0.2363; N2: ΔF1 -0.0243, Δprecisión +0.0685, Δrecuperación -0.1317. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`pacientes_XGB_pesos1`** frente a `pacientes_XGB_pesos0`: Sin pesos → pesos balanceados. F1 0,4465 → 0,4859 (Δ 0,0395); DE 0,0299; brecha 0,2974 (Δ -0,0615); entrenamiento 14,2974 s (Δ -0,1204 s). N3: ΔF1 +0.1424, Δprecisión -0.1284, Δrecuperación +0.3342; N2: ΔF1 -0.0455, Δprecisión +0.0911, Δrecuperación -0.1739. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

**Hiperparámetro**

- **`ajuste_RF_pesos0_max_depth_16`** frente a `pacientes_RF_pesos0`: max_depth=16. F1 0,3847 → 0,3519 (Δ -0,0328); DE 0,0272; brecha 0,5033 (Δ -0,1014); entrenamiento 9,6717 s (Δ -32,2101 s). N3: ΔF1 +0.0019, Δprecisión -0.0785, Δrecuperación +0.0015; REM: ΔF1 -0.0991, Δprecisión +0.0413, Δrecuperación -0.1305. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`ajuste_RF_pesos0_min_samples_leaf_10`** frente a `pacientes_RF_pesos0`: min_samples_leaf=10. F1 0,3847 → 0,3756 (Δ -0,0091); DE 0,0272; brecha 0,4489 (Δ -0,1558); entrenamiento 10,6526 s (Δ -31,2292 s). N3: ΔF1 +0.0243, Δprecisión -0.0300, Δrecuperación +0.0182; N1: ΔF1 -0.0328, Δprecisión -0.0371, Δrecuperación -0.0223. **Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`ajuste_RF_pesos1_max_depth_16`** frente a `pacientes_RF_pesos1`: max_depth=16. F1 0,4412 → 0,4530 (Δ 0,0118); DE 0,0351; brecha 0,4189 (Δ -0,1001); entrenamiento 8,1932 s (Δ -23,9919 s). N3: ΔF1 +0.0436, Δprecisión +0.0202, Δrecuperación +0.0565; N2: ΔF1 -0.0262, Δprecisión +0.0178, Δrecuperación -0.0614. **Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`ajuste_RF_pesos1_min_samples_leaf_10`** frente a `pacientes_RF_pesos1`: min_samples_leaf=10. F1 0,4412 → 0,4614 (Δ 0,0201); DE 0,0205; brecha 0,3761 (Δ -0,1430); entrenamiento 8,3861 s (Δ -23,7990 s). N3: ΔF1 +0.0908, Δprecisión -0.0680, Δrecuperación +0.2179; N2: ΔF1 -0.0278, Δprecisión +0.0281, Δrecuperación -0.0715. **Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`ajuste_XGB_pesos0_max_depth_2`** frente a `pacientes_XGB_pesos0`: max_depth=2. F1 0,4465 → 0,4276 (Δ -0,0189); DE 0,0352; brecha 0,2455 (Δ -0,1135); entrenamiento 3,8472 s (Δ -10,5706 s). REM: ΔF1 +0.0145, Δprecisión +0.0086, Δrecuperación +0.0122; N3: ΔF1 -0.0631, Δprecisión -0.1222, Δrecuperación -0.0379. **Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`ajuste_XGB_pesos0_reg_lambda_5`** frente a `pacientes_XGB_pesos0`: reg_lambda=5. F1 0,4465 → 0,4491 (Δ 0,0026); DE 0,0355; brecha 0,3507 (Δ -0,0082); entrenamiento 5,3580 s (Δ -9,0597 s). N1: ΔF1 +0.0065, Δprecisión +0.0177, Δrecuperación +0.0037; N2: ΔF1 +0.0005, Δprecisión +0.0012, Δrecuperación -0.0004. **Conclusión:** Mayor F1 promedio en 3/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`ajuste_XGB_pesos1_max_depth_2`** frente a `pacientes_XGB_pesos1`: max_depth=2. F1 0,4859 → 0,4611 (Δ -0,0248); DE 0,0333; brecha 0,1793 (Δ -0,1181); entrenamiento 9,1767 s (Δ -5,1206 s). REM: ΔF1 +0.0250, Δprecisión -0.0043, Δrecuperación +0.0697; N3: ΔF1 -0.0621, Δprecisión -0.1341, Δrecuperación +0.1674. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`ajuste_XGB_pesos1_reg_lambda_5`** frente a `pacientes_XGB_pesos1`: reg_lambda=5. F1 0,4859 → 0,4907 (Δ 0,0047); DE 0,0327; brecha 0,2879 (Δ -0,0095); entrenamiento 14,5448 s (Δ 0,2474 s). N1: ΔF1 +0.0073, Δprecisión +0.0069, Δrecuperación +0.0078; N2: ΔF1 +0.0017, Δprecisión +0.0005, Δrecuperación +0.0025. **Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

**Control**

- **`representacion_RF_candidata`** frente a `ajuste_RF_pesos1_min_samples_leaf_10`: candidata. F1 0,4614 → 0,4614 (Δ -0,0000); DE 0,0205; brecha 0,3761 (Δ 0,0000); entrenamiento 8,3861 s (Δ 0,0000 s). N3: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000; REM: ΔF1 -0.0000, Δprecisión +0.0000, Δrecuperación +0.0000. **Conclusión:** Repetición de la misma configuración y entradas; las diferencias de tiempo no son efecto de un hiperparámetro. **Decisión:** Usar como control de representación; no contar como mejora nueva.

- **`representacion_XGB_candidata`** frente a `ajuste_XGB_pesos1_reg_lambda_5`: candidata. F1 0,4907 → 0,4907 (Δ -0,0000); DE 0,0327; brecha 0,2879 (Δ 0,0000); entrenamiento 14,5448 s (Δ 0,0000 s). REM: ΔF1 +0.0000, Δprecisión -0.0000, Δrecuperación -0.0000; N1: ΔF1 -0.0000, Δprecisión +0.0000, Δrecuperación +0.0000. **Conclusión:** Repetición de la misma configuración y entradas; las diferencias de tiempo no son efecto de un hiperparámetro. **Decisión:** Usar como control de representación; no contar como mejora nueva.

**Representación**

- **`representacion_RF_separada_con_log`** frente a `ajuste_RF_pesos1_min_samples_leaf_10`: separada_con_log. F1 0,4614 → 0,4680 (Δ 0,0066); DE 0,0302; brecha 0,3731 (Δ -0,0029); entrenamiento 9,9561 s (Δ 1,5700 s). REM: ΔF1 +0.0128, Δprecisión +0.0105, Δrecuperación +0.0200; N3: ΔF1 -0.0036, Δprecisión -0.0128, Δrecuperación +0.0093. **Conclusión:** Mayor F1 promedio en 3/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`representacion_XGB_separada_con_log`** frente a `ajuste_XGB_pesos1_reg_lambda_5`: separada_con_log. F1 0,4907 → 0,4814 (Δ -0,0093); DE 0,0307; brecha 0,3025 (Δ 0,0147); entrenamiento 5,8685 s (Δ -8,6763 s). N2: ΔF1 +0.0016, Δprecisión +0.0010, Δrecuperación +0.0030; REM: ΔF1 -0.0178, Δprecisión -0.0034, Δrecuperación -0.0284. **Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

**Contexto temporal**

- **`contexto_pacientes_XGB_lag_1`** frente a `ajuste_XGB_pesos1_reg_lambda_5`: Historia 1 minutos. F1 0,4907 → 0,4964 (Δ 0,0058); DE 0,0331; brecha 0,3023 (Δ 0,0145); entrenamiento 8,8182 s (Δ -5,7265 s). REM: ΔF1 +0.0270, Δprecisión +0.0364, Δrecuperación +0.0229; N3: ΔF1 -0.0139, Δprecisión -0.0096, Δrecuperación -0.0198. **Conclusión:** Mayor F1 promedio en 3/5 folds; la brecha no se redujo claramente. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`contexto_pacientes_XGB_lag_2`** frente a `ajuste_XGB_pesos1_reg_lambda_5`: Historia 2 minutos. F1 0,4907 → 0,4940 (Δ 0,0033); DE 0,0330; brecha 0,3025 (Δ 0,0147); entrenamiento 8,6672 s (Δ -5,8776 s). REM: ΔF1 +0.0154, Δprecisión +0.0221, Δrecuperación +0.0084; N3: ΔF1 -0.0095, Δprecisión -0.0030, Δrecuperación -0.0167. **Conclusión:** Mayor F1 promedio en 3/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`contexto_pacientes_XGB_lag_5`** frente a `ajuste_XGB_pesos1_reg_lambda_5`: Historia 5 minutos. F1 0,4907 → 0,4881 (Δ -0,0026); DE 0,0352; brecha 0,3053 (Δ 0,0174); entrenamiento 18,9555 s (Δ 4,4107 s). N1: ΔF1 +0.0078, Δprecisión +0.0097, Δrecuperación +0.0063; N3: ΔF1 -0.0276, Δprecisión -0.0186, Δrecuperación -0.0400. **Conclusión:** Menor F1 promedio; mejoró en 3/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`contexto_pacientes_XGB_lag_10`** frente a `ajuste_XGB_pesos1_reg_lambda_5`: Historia 10 minutos. F1 0,4907 → 0,4916 (Δ 0,0009); DE 0,0279; brecha 0,3008 (Δ 0,0130); entrenamiento 20,7629 s (Δ 6,2182 s). N1: ΔF1 +0.0066, Δprecisión +0.0096, Δrecuperación +0.0049; N2: ΔF1 -0.0032, Δprecisión -0.0027, Δrecuperación -0.0020. **Conclusión:** Mayor F1 promedio en 3/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`contexto_pacientes_XGB_lag_15`** frente a `ajuste_XGB_pesos1_reg_lambda_5`: Historia 15 minutos. F1 0,4907 → 0,4927 (Δ 0,0021); DE 0,0329; brecha 0,2993 (Δ 0,0114); entrenamiento 8,5491 s (Δ -5,9957 s). REM: ΔF1 +0.0196, Δprecisión +0.0324, Δrecuperación +0.0129; N3: ΔF1 -0.0103, Δprecisión +0.0015, Δrecuperación -0.0239. **Conclusión:** Mayor F1 promedio en 4/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`contexto_pacientes_XGB_lag_5+10`** frente a `ajuste_XGB_pesos1_reg_lambda_5`: Historia 5+10 minutos. F1 0,4907 → 0,4893 (Δ -0,0014); DE 0,0371; brecha 0,3110 (Δ 0,0231); entrenamiento 12,6418 s (Δ -1,9030 s). REM: ΔF1 +0.0205, Δprecisión +0.0389, Δrecuperación +0.0170; N3: ΔF1 -0.0311, Δprecisión -0.0176, Δrecuperación -0.0498. **Conclusión:** Menor F1 promedio; mejoró en 3/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`contexto_pacientes_XGB_lag_1+2`** frente a `ajuste_XGB_pesos1_reg_lambda_5`: Historia 1+2 minutos (dos mejores individuales). F1 0,4907 → 0,5053 (Δ 0,0147); DE 0,0265; brecha 0,3010 (Δ 0,0131); entrenamiento 12,1839 s (Δ -2,3608 s). REM: ΔF1 +0.0377, Δprecisión +0.0295, Δrecuperación +0.0464; N3: ΔF1 +0.0002, Δprecisión +0.0131, Δrecuperación -0.0132. **Conclusión:** Mayor F1 promedio en 4/5 folds; la brecha no se redujo claramente. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

**Balanceo control**

- **`balanceo_pacientes_XGB_sin_pesos`** frente a `ajuste_XGB_pesos1_reg_lambda_5`: Misma configuración sin ponderación. F1 0,4907 → 0,4491 (Δ -0,0416); DE 0,0355; brecha 0,3507 (Δ 0,0628); entrenamiento 5,3580 s (Δ -9,1867 s). N2: ΔF1 +0.0443, Δprecisión -0.0904, Δrecuperación +0.1710; N3: ΔF1 -0.1444, Δprecisión +0.1251, Δrecuperación -0.3380. **Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`balanceo_pacientes_XGB_pesos`** frente a `balanceo_pacientes_XGB_sin_pesos`: Misma configuración con pesos balanceados. F1 0,4491 → 0,4907 (Δ 0,0416); DE 0,0327; brecha 0,2879 (Δ -0,0628); entrenamiento 14,5448 s (Δ 9,1867 s). N3: ΔF1 +0.1444, Δprecisión -0.1251, Δrecuperación +0.3380; N2: ΔF1 -0.0443, Δprecisión +0.0904, Δrecuperación -0.1710. **Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`balanceo_pacientes_XGB_escala`** frente a `balanceo_pacientes_XGB_sin_pesos`: Escalado sin remuestreo ni pesos. F1 0,4491 → 0,4451 (Δ -0,0040); DE 0,0332; brecha 0,3545 (Δ 0,0038); entrenamiento 5,4983 s (Δ 0,1403 s). N1: ΔF1 +0.0020, Δprecisión -0.0029, Δrecuperación +0.0027; N3: ΔF1 -0.0095, Δprecisión -0.0135, Δrecuperación -0.0090. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

**SMOTE**

- **`smote_pacientes_XGB_ratio0.5_k3`** frente a `balanceo_pacientes_XGB_escala`: SMOTE objetivo 50% de mayoritaria; k=3. F1 0,4451 → 0,4830 (Δ 0,0379); DE 0,0289; brecha 0,3147 (Δ -0,0399); entrenamiento 9,8013 s (Δ 4,3030 s). N3: ΔF1 +0.1351, Δprecisión -0.0666, Δrecuperación +0.2413; W: ΔF1 -0.0312, Δprecisión -0.0047, Δrecuperación -0.0552. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`smote_pacientes_XGB_ratio0.5_k5`** frente a `balanceo_pacientes_XGB_escala`: SMOTE objetivo 50% de mayoritaria; k=5. F1 0,4451 → 0,4818 (Δ 0,0367); DE 0,0210; brecha 0,3148 (Δ -0,0397); entrenamiento 8,3130 s (Δ 2,8146 s). N3: ΔF1 +0.1428, Δprecisión -0.0607, Δrecuperación +0.2436; W: ΔF1 -0.0364, Δprecisión -0.0106, Δrecuperación -0.0550. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`smote_pacientes_XGB_ratio1.0_k3`** frente a `balanceo_pacientes_XGB_escala`: SMOTE objetivo 100% de mayoritaria; k=3. F1 0,4451 → 0,4860 (Δ 0,0409); DE 0,0225; brecha 0,2911 (Δ -0,0635); entrenamiento 12,7084 s (Δ 7,2101 s). N3: ΔF1 +0.1501, Δprecisión -0.1005, Δrecuperación +0.3182; N2: ΔF1 -0.0424, Δprecisión +0.0856, Δrecuperación -0.1656. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`smote_pacientes_XGB_ratio1.0_k5`** frente a `balanceo_pacientes_XGB_escala`: SMOTE objetivo 100% de mayoritaria; k=5. F1 0,4451 → 0,4806 (Δ 0,0355); DE 0,0218; brecha 0,2926 (Δ -0,0620); entrenamiento 12,9639 s (Δ 7,4656 s). N3: ΔF1 +0.1414, Δprecisión -0.1133, Δrecuperación +0.3033; N2: ΔF1 -0.0454, Δprecisión +0.0823, Δrecuperación -0.1683. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### Epochs mezclados

**Pesos**

- **`epochs_Logistica_pesos1`** frente a `epochs_Logistica_pesos0`: Sin pesos → pesos balanceados. F1 0,2816 → 0,4061 (Δ 0,1245); DE 0,0026; brecha 0,0021 (Δ 0,0013); entrenamiento 2,0872 s (Δ -0,9688 s). REM: ΔF1 +0.3633, Δprecisión +0.0021, Δrecuperación +0.7262; N2: ΔF1 -0.1869, Δprecisión +0.2653, Δrecuperación -0.5533. **Conclusión:** Mayor F1 promedio en 5/5 folds; la brecha no se redujo claramente. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`epochs_RF_pesos1`** frente a `epochs_RF_pesos0`: Sin pesos → pesos balanceados. F1 0,7617 → 0,7860 (Δ 0,0243); DE 0,0081; brecha 0,1745 (Δ -0,0531); entrenamiento 8,3773 s (Δ -26,1677 s). N1: ΔF1 +0.1127, Δprecisión -0.1419, Δrecuperación +0.2509; N3: ΔF1 -0.0100, Δprecisión -0.1657, Δrecuperación +0.1419. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`epochs_XGB_pesos1`** frente a `epochs_XGB_pesos0`: Sin pesos → pesos balanceados. F1 0,7418 → 0,7273 (Δ -0,0145); DE 0,0052; brecha 0,0441 (Δ -0,0069); entrenamiento 5,4388 s (Δ 0,4929 s). N1: ΔF1 +0.0832, Δprecisión -0.1617, Δrecuperación +0.2937; N3: ΔF1 -0.1014, Δprecisión -0.2923, Δrecuperación +0.1753. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

**Protocolo**

- **`epochs_Baseline_pesos0`** frente a `pacientes_Baseline_pesos0`: Pacientes separados → Epochs mezclados. F1 0,1368 → 0,1371 (Δ 0,0003); DE 0,0000; brecha 0,0000 (Δ -0,0003); entrenamiento 0,0303 s (Δ -0,0342 s). N2: ΔF1 +0.0014, Δprecisión +0.0011, Δrecuperación +0.0000; W: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000. **Conclusión:** Cambia la separación de pacientes y epochs; la mezcla comparte personas y no demuestra mejor generalización. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

- **`epochs_Logistica_pesos0`** frente a `pacientes_Logistica_pesos0`: Pacientes separados → Epochs mezclados. F1 0,2610 → 0,2816 (Δ 0,0206); DE 0,0053; brecha 0,0008 (Δ -0,0367); entrenamiento 3,0561 s (Δ 0,1396 s). N3: ΔF1 +0.0406, Δprecisión +0.2226, Δrecuperación +0.0211; REM: ΔF1 -0.0035, Δprecisión +0.0772, Δrecuperación -0.0061. **Conclusión:** Cambia la separación de pacientes y epochs; la mezcla comparte personas y no demuestra mejor generalización. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

- **`epochs_Logistica_pesos1`** frente a `pacientes_Logistica_pesos1`: Pacientes separados → Epochs mezclados. F1 0,3467 → 0,4061 (Δ 0,0594); DE 0,0026; brecha 0,0021 (Δ -0,0708); entrenamiento 2,0872 s (Δ -0,2471 s). N1: ΔF1 +0.0842, Δprecisión +0.0593, Δrecuperación +0.0884; REM: ΔF1 +0.0275, Δprecisión +0.0069, Δrecuperación +0.0801. **Conclusión:** Cambia la separación de pacientes y epochs; la mezcla comparte personas y no demuestra mejor generalización. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

- **`epochs_RF_pesos0`** frente a `pacientes_RF_pesos0`: Pacientes separados → Epochs mezclados. F1 0,3847 → 0,7617 (Δ 0,3770); DE 0,0083; brecha 0,2276 (Δ -0,3771); entrenamiento 34,5450 s (Δ -7,3368 s). N3: ΔF1 +0.6578, Δprecisión +0.1192, Δrecuperación +0.6555; N2: ΔF1 +0.0946, Δprecisión +0.1137, Δrecuperación +0.0663. **Conclusión:** Cambia la separación de pacientes y epochs; la mezcla comparte personas y no demuestra mejor generalización. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

- **`epochs_RF_pesos1`** frente a `pacientes_RF_pesos1`: Pacientes separados → Epochs mezclados. F1 0,4412 → 0,7860 (Δ 0,3447); DE 0,0081; brecha 0,1745 (Δ -0,3446); entrenamiento 8,3773 s (Δ -23,8078 s). REM: ΔF1 +0.5335, Δprecisión +0.4968, Δrecuperación +0.5538; N2: ΔF1 +0.1121, Δprecisión +0.1218, Δrecuperación +0.1022. **Conclusión:** Cambia la separación de pacientes y epochs; la mezcla comparte personas y no demuestra mejor generalización. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

- **`epochs_XGB_pesos0`** frente a `pacientes_XGB_pesos0`: Pacientes separados → Epochs mezclados. F1 0,4465 → 0,7418 (Δ 0,2954); DE 0,0077; brecha 0,0510 (Δ -0,3080); entrenamiento 4,9458 s (Δ -9,4719 s). N3: ΔF1 +0.4717, Δprecisión +0.3049, Δrecuperación +0.5092; N2: ΔF1 +0.0726, Δprecisión +0.0772, Δrecuperación +0.0654. **Conclusión:** Cambia la separación de pacientes y epochs; la mezcla comparte personas y no demuestra mejor generalización. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

- **`epochs_XGB_pesos1`** frente a `pacientes_XGB_pesos1`: Pacientes separados → Epochs mezclados. F1 0,4859 → 0,7273 (Δ 0,2414); DE 0,0052; brecha 0,0441 (Δ -0,2533); entrenamiento 5,4388 s (Δ -8,8586 s). REM: ΔF1 +0.3791, Δprecisión +0.3271, Δrecuperación +0.4023; N2: ΔF1 +0.0741, Δprecisión +0.0771, Δrecuperación +0.0699. **Conclusión:** Cambia la separación de pacientes y epochs; la mezcla comparte personas y no demuestra mejor generalización. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

**Hiperparámetro**

- **`epochs_ajuste_RF_pesos0_max_depth_16`** frente a `epochs_RF_pesos0`: max_depth=16. F1 0,7617 → 0,6766 (Δ -0,0852); DE 0,0067; brecha 0,1652 (Δ -0,0624); entrenamiento 33,3766 s (Δ -1,1684 s). W: ΔF1 -0.0374, Δprecisión +0.0016, Δrecuperación -0.0745; REM: ΔF1 -0.1538, Δprecisión +0.0073, Δrecuperación -0.2456. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`epochs_ajuste_RF_pesos0_min_samples_leaf_10`** frente a `epochs_RF_pesos0`: min_samples_leaf=10. F1 0,7617 → 0,7071 (Δ -0,0546); DE 0,0076; brecha 0,1053 (Δ -0,1223); entrenamiento 26,0084 s (Δ -8,5366 s). N2: ΔF1 -0.0199, Δprecisión -0.0375, Δrecuperación +0.0043; N1: ΔF1 -0.1037, Δprecisión +0.0078, Δrecuperación -0.1030. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`epochs_ajuste_RF_pesos1_max_depth_16`** frente a `epochs_RF_pesos1`: max_depth=16. F1 0,7860 → 0,7215 (Δ -0,0645); DE 0,0064; brecha 0,1337 (Δ -0,0408); entrenamiento 7,2154 s (Δ -1,1619 s). N3: ΔF1 -0.0241, Δprecisión -0.0491, Δrecuperación +0.0153; REM: ΔF1 -0.1631, Δprecisión -0.2621, Δrecuperación +0.0040. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`epochs_ajuste_RF_pesos1_min_samples_leaf_10`** frente a `epochs_RF_pesos1`: min_samples_leaf=10. F1 0,7860 → 0,7303 (Δ -0,0556); DE 0,0059; brecha 0,0996 (Δ -0,0748); entrenamiento 7,4888 s (Δ -0,8885 s). W: ΔF1 -0.0335, Δprecisión -0.0160, Δrecuperación -0.0513; N3: ΔF1 -0.0910, Δprecisión -0.1571, Δrecuperación +0.0367. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`epochs_ajuste_XGB_pesos0_max_depth_2`** frente a `epochs_XGB_pesos0`: max_depth=2. F1 0,7418 → 0,6408 (Δ -0,1010); DE 0,0092; brecha 0,0156 (Δ -0,0353); entrenamiento 3,8709 s (Δ -1,0750 s). N2: ΔF1 -0.0329, Δprecisión -0.0539, Δrecuperación -0.0045; REM: ΔF1 -0.1483, Δprecisión -0.1209, Δrecuperación -0.1688. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`epochs_ajuste_XGB_pesos0_reg_lambda_5`** frente a `epochs_XGB_pesos0`: reg_lambda=5. F1 0,7418 → 0,7376 (Δ -0,0042); DE 0,0065; brecha 0,0499 (Δ -0,0010); entrenamiento 5,6363 s (Δ 0,6904 s). W: ΔF1 -0.0002, Δprecisión -0.0006, Δrecuperación +0.0003; N1: ΔF1 -0.0085, Δprecisión -0.0074, Δrecuperación -0.0081. **Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`epochs_ajuste_XGB_pesos1_max_depth_2`** frente a `epochs_XGB_pesos1`: max_depth=2. F1 0,7273 → 0,6119 (Δ -0,1154); DE 0,0073; brecha 0,0137 (Δ -0,0304); entrenamiento 4,0553 s (Δ -1,3834 s). N2: ΔF1 -0.0724, Δprecisión -0.0321, Δrecuperación -0.0956; N3: ΔF1 -0.1926, Δprecisión -0.2136, Δrecuperación -0.0044. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`epochs_ajuste_XGB_pesos1_reg_lambda_5`** frente a `epochs_XGB_pesos1`: reg_lambda=5. F1 0,7273 → 0,7231 (Δ -0,0042); DE 0,0055; brecha 0,0431 (Δ -0,0010); entrenamiento 5,4835 s (Δ 0,0447 s). W: ΔF1 -0.0019, Δprecisión -0.0014, Δrecuperación -0.0023; N1: ΔF1 -0.0061, Δprecisión -0.0056, Δrecuperación -0.0064. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

**Control**

- **`epochs_representacion_RF_candidata`** frente a `epochs_RF_pesos1`: candidata. F1 0,7860 → 0,7860 (Δ 0,0000); DE 0,0081; brecha 0,1745 (Δ 0,0000); entrenamiento 8,3773 s (Δ 0,0000 s). REM: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000; W: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000. **Conclusión:** Repetición de la misma configuración y entradas; las diferencias de tiempo no son efecto de un hiperparámetro. **Decisión:** Usar como control de representación; no contar como mejora nueva.

- **`epochs_representacion_XGB_candidata`** frente a `epochs_XGB_pesos0`: candidata. F1 0,7418 → 0,7418 (Δ 0,0000); DE 0,0077; brecha 0,0510 (Δ 0,0000); entrenamiento 4,9458 s (Δ 0,0000 s). REM: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000; W: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000. **Conclusión:** Repetición de la misma configuración y entradas; las diferencias de tiempo no son efecto de un hiperparámetro. **Decisión:** Usar como control de representación; no contar como mejora nueva.

**Representación**

- **`epochs_representacion_RF_separada_con_log`** frente a `epochs_RF_pesos1`: separada_con_log. F1 0,7860 → 0,7835 (Δ -0,0024); DE 0,0072; brecha 0,1781 (Δ 0,0036); entrenamiento 11,6642 s (Δ 3,2869 s). N3: ΔF1 +0.0027, Δprecisión +0.0046, Δrecuperación +0.0000; N1: ΔF1 -0.0063, Δprecisión -0.0026, Δrecuperación -0.0105. **Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`epochs_representacion_XGB_separada_con_log`** frente a `epochs_XGB_pesos0`: separada_con_log. F1 0,7418 → 0,7424 (Δ 0,0006); DE 0,0087; brecha 0,0548 (Δ 0,0039); entrenamiento 5,7990 s (Δ 0,8531 s). REM: ΔF1 +0.0048, Δprecisión +0.0059, Δrecuperación +0.0038; N3: ΔF1 -0.0038, Δprecisión -0.0071, Δrecuperación -0.0011. **Conclusión:** Mayor F1 promedio en 3/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

**Contexto temporal**

- **`contexto_epochs_RF_lag_1`** frente a `epochs_RF_pesos1`: Historia 1 minutos. F1 0,7860 → 0,7854 (Δ -0,0005); DE 0,0061; brecha 0,1822 (Δ 0,0078); entrenamiento 13,7773 s (Δ 5,4000 s). N3: ΔF1 +0.0157, Δprecisión +0.0245, Δrecuperación +0.0033; N1: ΔF1 -0.0145, Δprecisión -0.0017, Δrecuperación -0.0292. **Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`contexto_epochs_RF_lag_2`** frente a `epochs_RF_pesos1`: Historia 2 minutos. F1 0,7860 → 0,7802 (Δ -0,0057); DE 0,0087; brecha 0,1868 (Δ 0,0124); entrenamiento 13,7927 s (Δ 5,4154 s). N3: ΔF1 +0.0138, Δprecisión +0.0192, Δrecuperación +0.0060; N1: ΔF1 -0.0172, Δprecisión -0.0029, Δrecuperación -0.0333. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`contexto_epochs_RF_lag_5`** frente a `epochs_RF_pesos1`: Historia 5 minutos. F1 0,7860 → 0,7795 (Δ -0,0065); DE 0,0060; brecha 0,1877 (Δ 0,0132); entrenamiento 13,4848 s (Δ 5,1075 s). N3: ΔF1 +0.0044, Δprecisión +0.0095, Δrecuperación -0.0027; N1: ΔF1 -0.0161, Δprecisión -0.0020, Δrecuperación -0.0322. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`contexto_epochs_RF_lag_10`** frente a `epochs_RF_pesos1`: Historia 10 minutos. F1 0,7860 → 0,7841 (Δ -0,0019); DE 0,0062; brecha 0,1827 (Δ 0,0082); entrenamiento 13,2830 s (Δ 4,9057 s). N3: ΔF1 +0.0085, Δprecisión +0.0121, Δrecuperación +0.0033; N1: ΔF1 -0.0112, Δprecisión +0.0023, Δrecuperación -0.0267. **Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`contexto_epochs_RF_lag_15`** frente a `epochs_RF_pesos1`: Historia 15 minutos. F1 0,7860 → 0,7888 (Δ 0,0029); DE 0,0045; brecha 0,1777 (Δ 0,0032); entrenamiento 13,6455 s (Δ 5,2682 s). REM: ΔF1 +0.0055, Δprecisión -0.0030, Δrecuperación +0.0153; W: ΔF1 -0.0004, Δprecisión +0.0027, Δrecuperación -0.0036. **Conclusión:** Mayor F1 promedio en 4/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`contexto_epochs_RF_lag_5+10`** frente a `epochs_RF_pesos1`: Historia 5+10 minutos. F1 0,7860 → 0,7795 (Δ -0,0064); DE 0,0064; brecha 0,1910 (Δ 0,0165); entrenamiento 17,6509 s (Δ 9,2736 s). N3: ΔF1 +0.0056, Δprecisión +0.0133, Δrecuperación -0.0049; N1: ΔF1 -0.0209, Δprecisión +0.0000, Δrecuperación -0.0443. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`contexto_epochs_RF_lag_1+15`** frente a `epochs_RF_pesos1`: Historia 1+15 minutos (dos mejores individuales). F1 0,7860 → 0,7852 (Δ -0,0008); DE 0,0053; brecha 0,1851 (Δ 0,0106); entrenamiento 18,1138 s (Δ 9,7364 s). N3: ΔF1 +0.0125, Δprecisión +0.0207, Δrecuperación +0.0011; N1: ΔF1 -0.0104, Δprecisión +0.0042, Δrecuperación -0.0271. **Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

**Balanceo control**

- **`balanceo_epochs_RF_sin_pesos`** frente a `epochs_RF_pesos1`: Misma configuración sin ponderación. F1 0,7860 → 0,7617 (Δ -0,0243); DE 0,0083; brecha 0,2276 (Δ 0,0531); entrenamiento 34,5450 s (Δ 26,1677 s). N3: ΔF1 +0.0100, Δprecisión +0.1657, Δrecuperación -0.1419; N1: ΔF1 -0.1127, Δprecisión +0.1419, Δrecuperación -0.2509. **Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

- **`balanceo_epochs_RF_pesos`** frente a `balanceo_epochs_RF_sin_pesos`: Misma configuración con pesos balanceados. F1 0,7617 → 0,7860 (Δ 0,0243); DE 0,0081; brecha 0,1745 (Δ -0,0531); entrenamiento 8,3773 s (Δ -26,1677 s). N1: ΔF1 +0.1127, Δprecisión -0.1419, Δrecuperación +0.2509; N3: ΔF1 -0.0100, Δprecisión -0.1657, Δrecuperación +0.1419. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`balanceo_epochs_RF_escala`** frente a `balanceo_epochs_RF_sin_pesos`: Escalado sin remuestreo ni pesos. F1 0,7617 → 0,7645 (Δ 0,0028); DE 0,0112; brecha 0,2245 (Δ -0,0031); entrenamiento 12,5734 s (Δ -21,9716 s). N1: ΔF1 +0.0136, Δprecisión +0.0112, Δrecuperación +0.0124; REM: ΔF1 -0.0083, Δprecisión -0.0105, Δrecuperación -0.0064. **Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

**SMOTE**

- **`smote_epochs_RF_ratio0.5_k3`** frente a `balanceo_epochs_RF_escala`: SMOTE objetivo 50% de mayoritaria; k=3. F1 0,7645 → 0,7924 (Δ 0,0279); DE 0,0089; brecha 0,2028 (Δ -0,0217); entrenamiento 20,3864 s (Δ 7,8131 s). N1: ΔF1 +0.0939, Δprecisión -0.0927, Δrecuperación +0.1708; N2: ΔF1 +0.0045, Δprecisión +0.0398, Δrecuperación -0.0366. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`smote_epochs_RF_ratio0.5_k5`** frente a `balanceo_epochs_RF_escala`: SMOTE objetivo 50% de mayoritaria; k=5. F1 0,7645 → 0,7910 (Δ 0,0265); DE 0,0081; brecha 0,2040 (Δ -0,0205); entrenamiento 20,6019 s (Δ 8,0285 s). N1: ΔF1 +0.0866, Δprecisión -0.1024, Δrecuperación +0.1654; N2: ΔF1 +0.0042, Δprecisión +0.0395, Δrecuperación -0.0370. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`smote_epochs_RF_ratio1.0_k3`** frente a `balanceo_epochs_RF_escala`: SMOTE objetivo 100% de mayoritaria; k=3. F1 0,7645 → 0,7995 (Δ 0,0349); DE 0,0059; brecha 0,1958 (Δ -0,0287); entrenamiento 38,7379 s (Δ 26,1645 s). N1: ΔF1 +0.1121, Δprecisión -0.1396, Δrecuperación +0.2511; N2: ΔF1 +0.0014, Δprecisión +0.0738, Δrecuperación -0.0763. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

- **`smote_epochs_RF_ratio1.0_k5`** frente a `balanceo_epochs_RF_escala`: SMOTE objetivo 100% de mayoritaria; k=5. F1 0,7645 → 0,8006 (Δ 0,0360); DE 0,0038; brecha 0,1947 (Δ -0,0298); entrenamiento 38,1493 s (Δ 25,5759 s). N1: ΔF1 +0.1186, Δprecisión -0.1411, Δrecuperación +0.2675; N2: ΔF1 +0.0008, Δprecisión +0.0768, Δrecuperación -0.0803. **Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

### Comparación posterior en test histórico

En los mismos 16 pacientes, el candidato seleccionado mediante **pacientes separados** obtuvo el mayor F1 macro. Diferencia epochs menos pacientes: **-0,0426**. Las validaciones no se comparan como si midieran generalización equivalente. La diferencia en test corresponde a estos candidatos concretos; pueden cambiar algoritmo, entradas y parámetros además del protocolo. No se realizaron reajustes posteriores.

El test ya había sido consultado y tuvo exposición histórica en EDA/comparaciones de la cohorte completa. Esta es una comparación posterior sobre personas excluidas de los nuevos entrenamientos, **no una nueva prueba independiente**. No se usó para seleccionar ni reajustar los candidatos de esta ronda. La selección entre muchas pruebas puede optimizar en exceso la validación.

Al mezclar epochs se comparten personas y observaciones próximas. Con historia, un antecedente puede contener señales de otro fold; no contiene su etiqueta, pero la dependencia puede favorecer las métricas. Las etapas ausentes y las distintas duraciones limitan comparaciones individuales. Los modelos utilizan wearable + PSG; no demuestran rendimiento solo wearable.

## Evidencia histórica · notebook oficial previo

Lo siguiente conserva parámetros y resultados de otra ronda, incluidos otros protocolos. No es el estado activo ni una comparación controlada con la revisión.



Lo siguiente conserva parámetros y resultados de otra ronda, incluidos otros protocolos. No es el estado activo ni una comparación controlada con la revisión.

El [notebook](../../temporal_version_tp_entrega03.ipynb) define las configuraciones y exporta las salidas completas. Esta guía mantiene interpretación y conclusiones. Los valores son candidatos, no óptimos comprobados.

## Método

Reservar test por paciente; comparar protocolos con parámetros fijos y seleccionar por separado para personas nuevas y futuras lecturas de pacientes conocidos. Variar un parámetro por vez respecto de la referencia, sin/con pesos. Revisar F1 macro train/validación, brecha, desviación, precisión/recuperación/F1 de todas las etapas y tiempo. Las combinaciones simultáneas de hiperparámetros quedan para otra ronda. No ejecutar producto cartesiano completo. No consultar test para elegir.

## Parámetros

| Modelo | Parámetro | Referencia → variaciones | Efecto esperado, no garantizado |
| --- | --- | --- | --- |
| Logística | C | 1 → 0.01, 0.1, 10 | Menor: mayor regularización y posible sesgo; mayor: más flexibilidad y posible sobreajuste. |
| Logística | solver, max_iter, tol | lbfgs, 2000, tolerancia de biblioteca; fijos | Optimización y convergencia; más iteraciones no agregan capacidad. Escalar dentro del fold. |
| RF | max_depth | None → 8, 16 | Limitar profundidad reduce capacidad y puede reducir costo/sobreajuste. |
| RF | min_samples_leaf | 2 → 10, 30 | Suaviza, puede perder patrones minoritarios. |
| RF | max_features | sqrt → 0.5 | Cambia diversidad/fuerza de árboles y costo. |
| RF | n_estimators | 200 → 100, 400 | Más árboles estabilizan promedio, aumentan tiempo/memoria; no corrigen solos sobreajuste. |
| RF | min_samples_split | Predeterminado, fijo | Aumentarlo restringe divisiones; alternativa posterior. |
| XGB | max_depth | 4 → 2, 6 | Mayor: más capacidad, costo y posible sobreajuste. |
| XGB | min_child_weight | Predeterminado → 5, 15 | Restringe divisiones por suma de hessianos, no conteo de filas. |
| XGB | learning_rate | 0.1 → 0.03 | Menor aporte por ronda; suele requerir más rondas. |
| XGB | n_estimators | 200 → 100, 400 | Más rondas: más tiempo y posible sobreajuste; combinar luego con learning_rate. |
| XGB | reg_lambda | Predeterminado → 5, 10 | L2 sobre valores de hojas: más restricción, posible mayor sesgo. |
| XGB | subsample, colsample_bytree | 0.8 → 1.0, por separado | Cambia aleatoriedad/regularización y costo. |
| XGB | gamma, reg_alpha | Predeterminados, fijos | Mejora mínima para dividir y penalización L1; segunda ronda si se justifica. |
| Todos | Pesos | Sin / balanceados por observación | Mayor costo de errores minoritarios; puede aumentar falsos positivos. |

`random_state=42` permite reproducir; `n_jobs=-1` paraleliza. No se optimizan como capacidad. XGB mantiene cinco clases, `multi:softprob`, `hist` y métrica interna `mlogloss`; seleccionamos por F1 macro. No hay early stopping: requeriría validación interna acorde al escenario, sin usar el fold evaluado para detenerse. Se guardan versiones porque los valores predeterminados pueden cambiar.

Fuentes externas: [Logística](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html), [RF](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html), [XGBoost](https://xgboost.readthedocs.io/en/stable/parameter.html).

## Contexto y balanceo: parámetros adicionales

| Prueba | Valores | Efecto esperado, no demostrado antes de ejecutar |
| --- | --- | --- |
| Historia individual | 1, 2, 5, 10, 15 minutos | Puede aportar contexto de señales o agregar ruido y dimensiones. |
| Historia conjunta | 5+10 y dos mejores individuales | Puede sumar información o redundancia; selección sobre desarrollo. |
| Faltantes | NaN + disponibilidad; mediana de entrenamiento | Conserva epochs sin antecedentes. Indicadores pueden representar tiempo transcurrido, no solo fisiología. |
| SMOTE: vecinos | 3, 5 | Pocos: interpolación local; más: mezcla más amplia. No garantiza plausibilidad fisiológica. |
| SMOTE: cantidades | 50/100 % de la mayoritaria por clase | Más ejemplos sintéticos y costo; puede cambiar precisión/recuperación. No reducir clases ya mayores al objetivo. |

SMOTE usa escala aprendida en entrenamiento y se compara con un control escalado sin remuestreo. No combina pesos ni historia temporal. Las métricas de entrenamiento usan observaciones reales. [Documentación de SMOTE](https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTE.html), [prevención de filtraciones](https://imbalanced-learn.org/stable/common_pitfalls.html).

## Resultados ejecutados por escenario

Dos escenarios de selección, sin consultar el test. Desarrollo: 45.011 epochs de 60 pacientes; reserva: 11.839 epochs de 16 pacientes. El protocolo por pacientes evalúa todos los epochs de desarrollo. El cronológico evalúa 37.490 epochs; excluye de validación los 7.521 del bloque inicial, conservados para entrenamiento. Cinco folds por escenario; gap cronológico de 15 minutos.

Se ejecutaron 147 comparaciones documentadas: Hiperparámetro: 84, Protocolo: 14, Contexto temporal: 14, Pesos: 9, SMOTE: 8, Representación: 8, Balanceo control: 6, Control: 4. Las referencias de epochs mezclados se conservan como diagnóstico. Las cifras son de desarrollo, no de prueba final.

Δ significa prueba menos referencia. Cada ensayo mantiene sus folds, modelo y entradas salvo el factor declarado. Tiempos observados, dependientes del equipo y carga. “Prácticamente igual” indica |ΔF1| < 0,0005 solo para presentar; no es significación estadística. Menor brecha no implica mejor predicción. Los folds de protocolos distintos no están pareados ni tienen la misma población evaluada.

### Personas nuevas

Referencia trivial: F1 macro 0.1368; exactitud 0.5201. No distingue todas las etapas.

#### 01. Regresión logística · Pesos · Sin pesos → pesos balanceados

Prueba: `pacientes_Logistica_pesos1`. Referencia: `pacientes_Logistica_pesos0`. Con pesos.

F1 macro **0.2610 → 0.3467 ± 0.0390** (Δ +0.0857). F1 entrenamiento 0.4196; brecha 0.0729 (Δ +0.0354). Entrenamiento total 2.33 s (Δ -0.61 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.3323, Δprecisión +0.0723, Δrecuperación +0.6400; N2: ΔF1 -0.2359, Δprecisión +0.1961, Δrecuperación -0.5756.

**Conclusión:** Mayor F1 promedio en 5/5 folds; la brecha no se redujo claramente. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 02. Random Forest · Pesos · Sin pesos → pesos balanceados

Prueba: `pacientes_RF_pesos1`. Referencia: `pacientes_RF_pesos0`. Con pesos.

F1 macro **0.3847 → 0.4412 ± 0.0288** (Δ +0.0565). F1 entrenamiento 0.9603; brecha 0.5190 (Δ -0.0857). Entrenamiento total 37.20 s (Δ -8.49 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.2340, Δprecisión -0.2604, Δrecuperación +0.2363; N2: ΔF1 -0.0243, Δprecisión +0.0685, Δrecuperación -0.1317.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 03. XGBoost · Pesos · Sin pesos → pesos balanceados

Prueba: `pacientes_XGB_pesos1`. Referencia: `pacientes_XGB_pesos0`. Con pesos.

F1 macro **0.4465 → 0.4859 ± 0.0299** (Δ +0.0395). F1 entrenamiento 0.7833; brecha 0.2974 (Δ -0.0615). Entrenamiento total 16.36 s (Δ -4.73 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1424, Δprecisión -0.1284, Δrecuperación +0.3342; N2: ΔF1 -0.0455, Δprecisión +0.0911, Δrecuperación -0.1739.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 04. Regresión logística · Hiperparámetro · C=0.01

Prueba: `ajuste_Logistica_pesos0_C_0.01`. Referencia: `pacientes_Logistica_pesos0`. Sin pesos.

F1 macro **0.2610 → 0.2490 ± 0.0209** (Δ -0.0120). F1 entrenamiento 0.2693; brecha 0.0203 (Δ -0.0172). Entrenamiento total 0.76 s (Δ -2.17 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: W: ΔF1 +0.0028, Δprecisión +0.0061, Δrecuperación +0.0006; REM: ΔF1 -0.0317, Δprecisión -0.0464, Δrecuperación -0.0213.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 05. Regresión logística · Hiperparámetro · C=0.1

Prueba: `ajuste_Logistica_pesos0_C_0.1`. Referencia: `pacientes_Logistica_pesos0`. Sin pesos.

F1 macro **0.2610 → 0.2563 ± 0.0212** (Δ -0.0047). F1 entrenamiento 0.2924; brecha 0.0361 (Δ -0.0014). Entrenamiento total 1.43 s (Δ -1.50 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: W: ΔF1 +0.0006, Δprecisión +0.0006, Δrecuperación +0.0005; N3: ΔF1 -0.0165, Δprecisión -0.0392, Δrecuperación -0.0107.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 06. Regresión logística · Hiperparámetro · C=10

Prueba: `ajuste_Logistica_pesos0_C_10`. Referencia: `pacientes_Logistica_pesos0`. Sin pesos.

F1 macro **0.2610 → 0.2612 ± 0.0198** (Δ +0.0002). F1 entrenamiento 0.2992; brecha 0.0380 (Δ +0.0005). Entrenamiento total 1.52 s (Δ -1.42 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0008, Δprecisión +0.0016, Δrecuperación +0.0005; W: ΔF1 -0.0002, Δprecisión -0.0002, Δrecuperación -0.0002.

**Conclusión:** F1 promedio prácticamente igual en esta ronda; no hay una ventaja predictiva clara. **Decisión:** Sin prioridad frente a la referencia por F1 macro.

#### 07. Regresión logística · Hiperparámetro · C=0.01

Prueba: `ajuste_Logistica_pesos1_C_0.01`. Referencia: `pacientes_Logistica_pesos1`. Con pesos.

F1 macro **0.3467 → 0.3334 ± 0.0407** (Δ -0.0132). F1 entrenamiento 0.4053; brecha 0.0718 (Δ -0.0011). Entrenamiento total 0.69 s (Δ -1.64 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: W: ΔF1 +0.0034, Δprecisión +0.0039, Δrecuperación +0.0027; N2: ΔF1 -0.0404, Δprecisión -0.0051, Δrecuperación -0.0406.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 08. Regresión logística · Hiperparámetro · C=0.1

Prueba: `ajuste_Logistica_pesos1_C_0.1`. Referencia: `pacientes_Logistica_pesos1`. Con pesos.

F1 macro **0.3467 → 0.3446 ± 0.0392** (Δ -0.0021). F1 entrenamiento 0.4177; brecha 0.0731 (Δ +0.0002). Entrenamiento total 1.04 s (Δ -1.29 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: W: ΔF1 +0.0003, Δprecisión +0.0001, Δrecuperación +0.0005; N2: ΔF1 -0.0068, Δprecisión -0.0013, Δrecuperación -0.0069.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 09. Regresión logística · Hiperparámetro · C=10

Prueba: `ajuste_Logistica_pesos1_C_10`. Referencia: `pacientes_Logistica_pesos1`. Con pesos.

F1 macro **0.3467 → 0.3469 ± 0.0388** (Δ +0.0002). F1 entrenamiento 0.4198; brecha 0.0729 (Δ +0.0000). Entrenamiento total 1.22 s (Δ -1.11 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N2: ΔF1 +0.0007, Δprecisión -0.0000, Δrecuperación +0.0007; REM: ΔF1 -0.0002, Δprecisión -0.0002, Δrecuperación -0.0002.

**Conclusión:** F1 promedio prácticamente igual en esta ronda; no hay una ventaja predictiva clara. **Decisión:** Sin prioridad frente a la referencia por F1 macro.

#### 10. Random Forest · Hiperparámetro · max_depth=8

Prueba: `ajuste_RF_pesos0_max_depth_8`. Referencia: `pacientes_RF_pesos0`. Sin pesos.

F1 macro **0.3847 → 0.2726 ± 0.0348** (Δ -0.1121). F1 entrenamiento 0.4224; brecha 0.1498 (Δ -0.4549). Entrenamiento total 5.59 s (Δ -40.10 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: W: ΔF1 -0.0178, Δprecisión +0.1093, Δrecuperación -0.1270; REM: ΔF1 -0.3455, Δprecisión -0.3451, Δrecuperación -0.3083.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 11. Random Forest · Hiperparámetro · max_depth=16

Prueba: `ajuste_RF_pesos0_max_depth_16`. Referencia: `pacientes_RF_pesos0`. Sin pesos.

F1 macro **0.3847 → 0.3519 ± 0.0272** (Δ -0.0328). F1 entrenamiento 0.8552; brecha 0.5033 (Δ -0.1014). Entrenamiento total 9.75 s (Δ -35.94 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0019, Δprecisión -0.0785, Δrecuperación +0.0015; REM: ΔF1 -0.0991, Δprecisión +0.0413, Δrecuperación -0.1305.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 12. Random Forest · Hiperparámetro · min_samples_leaf=10

Prueba: `ajuste_RF_pesos0_min_samples_leaf_10`. Referencia: `pacientes_RF_pesos0`. Sin pesos.

F1 macro **0.3847 → 0.3756 ± 0.0272** (Δ -0.0091). F1 entrenamiento 0.8245; brecha 0.4489 (Δ -0.1558). Entrenamiento total 11.00 s (Δ -34.68 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0243, Δprecisión -0.0300, Δrecuperación +0.0182; N1: ΔF1 -0.0328, Δprecisión -0.0371, Δrecuperación -0.0223.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 13. Random Forest · Hiperparámetro · min_samples_leaf=30

Prueba: `ajuste_RF_pesos0_min_samples_leaf_30`. Referencia: `pacientes_RF_pesos0`. Sin pesos.

F1 macro **0.3847 → 0.3628 ± 0.0253** (Δ -0.0219). F1 entrenamiento 0.6967; brecha 0.3340 (Δ -0.2707). Entrenamiento total 9.67 s (Δ -36.01 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0306, Δprecisión -0.0108, Δrecuperación +0.0215; REM: ΔF1 -0.0614, Δprecisión -0.0336, Δrecuperación -0.0703.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 14. Random Forest · Hiperparámetro · max_features=0.5

Prueba: `ajuste_RF_pesos0_max_features_0.5`. Referencia: `pacientes_RF_pesos0`. Sin pesos.

F1 macro **0.3847 → 0.4156 ± 0.0232** (Δ +0.0309). F1 entrenamiento 0.9914; brecha 0.5758 (Δ -0.0289). Entrenamiento total 31.03 s (Δ -14.66 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1069, Δprecisión -0.0317, Δrecuperación +0.0767; N2: ΔF1 +0.0023, Δprecisión +0.0132, Δrecuperación -0.0137.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. Cambia cuántas variables compiten por división y la diversidad de árboles. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 15. Random Forest · Hiperparámetro · n_estimators=100

Prueba: `ajuste_RF_pesos0_n_estimators_100`. Referencia: `pacientes_RF_pesos0`. Sin pesos.

F1 macro **0.3847 → 0.3792 ± 0.0270** (Δ -0.0055). F1 entrenamiento 0.9885; brecha 0.6093 (Δ +0.0046). Entrenamiento total 13.05 s (Δ -32.64 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0060, Δprecisión +0.0187, Δrecuperación +0.0038; N3: ΔF1 -0.0148, Δprecisión -0.0694, Δrecuperación -0.0085.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 16. Random Forest · Hiperparámetro · n_estimators=400

Prueba: `ajuste_RF_pesos0_n_estimators_400`. Referencia: `pacientes_RF_pesos0`. Sin pesos.

F1 macro **0.3847 → 0.3862 ± 0.0269** (Δ +0.0015). F1 entrenamiento 0.9897; brecha 0.6035 (Δ -0.0012). Entrenamiento total 87.51 s (Δ +41.83 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0079, Δprecisión +0.0151, Δrecuperación +0.0049; REM: ΔF1 -0.0023, Δprecisión -0.0076, Δrecuperación -0.0017.

**Conclusión:** Mayor F1 promedio en 3/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 17. Random Forest · Hiperparámetro · max_depth=8

Prueba: `ajuste_RF_pesos1_max_depth_8`. Referencia: `pacientes_RF_pesos1`. Con pesos.

F1 macro **0.4412 → 0.4055 ± 0.0311** (Δ -0.0357). F1 entrenamiento 0.5896; brecha 0.1841 (Δ -0.3350). Entrenamiento total 18.22 s (Δ -18.98 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0672, Δprecisión -0.1684, Δrecuperación +0.3417; N2: ΔF1 -0.1844, Δprecisión -0.0110, Δrecuperación -0.2810.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 18. Random Forest · Hiperparámetro · max_depth=16

Prueba: `ajuste_RF_pesos1_max_depth_16`. Referencia: `pacientes_RF_pesos1`. Con pesos.

F1 macro **0.4412 → 0.4530 ± 0.0351** (Δ +0.0118). F1 entrenamiento 0.8719; brecha 0.4189 (Δ -0.1001). Entrenamiento total 30.13 s (Δ -7.07 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0436, Δprecisión +0.0202, Δrecuperación +0.0565; N2: ΔF1 -0.0262, Δprecisión +0.0178, Δrecuperación -0.0614.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 19. Random Forest · Hiperparámetro · min_samples_leaf=10

Prueba: `ajuste_RF_pesos1_min_samples_leaf_10`. Referencia: `pacientes_RF_pesos1`. Con pesos.

F1 macro **0.4412 → 0.4614 ± 0.0205** (Δ +0.0201). F1 entrenamiento 0.8375; brecha 0.3761 (Δ -0.1430). Entrenamiento total 11.22 s (Δ -25.98 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0908, Δprecisión -0.0680, Δrecuperación +0.2179; N2: ΔF1 -0.0278, Δprecisión +0.0281, Δrecuperación -0.0715.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 20. Random Forest · Hiperparámetro · min_samples_leaf=30

Prueba: `ajuste_RF_pesos1_min_samples_leaf_30`. Referencia: `pacientes_RF_pesos1`. Con pesos.

F1 macro **0.4412 → 0.4483 ± 0.0352** (Δ +0.0071). F1 entrenamiento 0.7278; brecha 0.2795 (Δ -0.2396). Entrenamiento total 6.77 s (Δ -30.43 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0723, Δprecisión -0.1645, Δrecuperación +0.3564; N2: ΔF1 -0.0635, Δprecisión +0.0340, Δrecuperación -0.1320.

**Conclusión:** Mayor F1 promedio en 3/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 21. Random Forest · Hiperparámetro · max_features=0.5

Prueba: `ajuste_RF_pesos1_max_features_0.5`. Referencia: `pacientes_RF_pesos1`. Con pesos.

F1 macro **0.4412 → 0.4476 ± 0.0192** (Δ +0.0064). F1 entrenamiento 0.9612; brecha 0.5136 (Δ -0.0055). Entrenamiento total 88.52 s (Δ +51.32 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0348, Δprecisión -0.0023, Δrecuperación +0.0586; W: ΔF1 -0.0108, Δprecisión -0.0056, Δrecuperación -0.0203.

**Conclusión:** Mayor F1 promedio en 3/5 folds; también se redujo la brecha. Cambia cuántas variables compiten por división y la diversidad de árboles. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 22. Random Forest · Hiperparámetro · n_estimators=100

Prueba: `ajuste_RF_pesos1_n_estimators_100`. Referencia: `pacientes_RF_pesos1`. Con pesos.

F1 macro **0.4412 → 0.4394 ± 0.0268** (Δ -0.0018). F1 entrenamiento 0.9594; brecha 0.5199 (Δ +0.0009). Entrenamiento total 17.41 s (Δ -19.78 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0018, Δprecisión -0.0101, Δrecuperación +0.0064; N2: ΔF1 -0.0044, Δprecisión -0.0021, Δrecuperación -0.0066.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 23. Random Forest · Hiperparámetro · n_estimators=400

Prueba: `ajuste_RF_pesos1_n_estimators_400`. Referencia: `pacientes_RF_pesos1`. Con pesos.

F1 macro **0.4412 → 0.4451 ± 0.0247** (Δ +0.0039). F1 entrenamiento 0.9611; brecha 0.5160 (Δ -0.0030). Entrenamiento total 70.01 s (Δ +32.81 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0147, Δprecisión +0.0122, Δrecuperación +0.0175; N1: ΔF1 -0.0058, Δprecisión -0.0017, Δrecuperación -0.0063.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 24. XGBoost · Hiperparámetro · max_depth=2

Prueba: `ajuste_XGB_pesos0_max_depth_2`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.4276 ± 0.0352** (Δ -0.0189). F1 entrenamiento 0.6730; brecha 0.2455 (Δ -0.1135). Entrenamiento total 13.58 s (Δ -7.50 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0145, Δprecisión +0.0086, Δrecuperación +0.0122; N3: ΔF1 -0.0631, Δprecisión -0.1222, Δrecuperación -0.0379.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 25. XGBoost · Hiperparámetro · max_depth=6

Prueba: `ajuste_XGB_pesos0_max_depth_6`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.4327 ± 0.0294** (Δ -0.0137). F1 entrenamiento 0.9217; brecha 0.4890 (Δ +0.1301). Entrenamiento total 26.23 s (Δ +5.15 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0136, Δprecisión -0.0149, Δrecuperación +0.0163; REM: ΔF1 -0.0559, Δprecisión -0.0401, Δrecuperación -0.0722.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 26. XGBoost · Hiperparámetro · min_child_weight=5

Prueba: `ajuste_XGB_pesos0_min_child_weight_5`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.4475 ± 0.0280** (Δ +0.0011). F1 entrenamiento 0.8009; brecha 0.3534 (Δ -0.0055). Entrenamiento total 19.29 s (Δ -1.79 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0093, Δprecisión +0.0077, Δrecuperación +0.0063; REM: ΔF1 -0.0050, Δprecisión -0.0163, Δrecuperación +0.0007.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 27. XGBoost · Hiperparámetro · min_child_weight=15

Prueba: `ajuste_XGB_pesos0_min_child_weight_15`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.4474 ± 0.0358** (Δ +0.0010). F1 entrenamiento 0.7955; brecha 0.3481 (Δ -0.0108). Entrenamiento total 16.27 s (Δ -4.82 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0132, Δprecisión +0.0037, Δrecuperación +0.0108; REM: ΔF1 -0.0050, Δprecisión -0.0211, Δrecuperación +0.0020.

**Conclusión:** Mayor F1 promedio en 2/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 28. XGBoost · Hiperparámetro · learning_rate=0.03

Prueba: `ajuste_XGB_pesos0_learning_rate_0.03`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.4178 ± 0.0315** (Δ -0.0287). F1 entrenamiento 0.7055; brecha 0.2877 (Δ -0.0712). Entrenamiento total 18.42 s (Δ -2.66 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0001, Δprecisión +0.0143, Δrecuperación +0.0071; N3: ΔF1 -0.0635, Δprecisión -0.0629, Δrecuperación -0.0536.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. La tasa se cambió con rondas fijas; una tasa menor podría necesitar más rondas, combinación no probada. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 29. XGBoost · Hiperparámetro · n_estimators=100

Prueba: `ajuste_XGB_pesos0_n_estimators_100`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.4387 ± 0.0335** (Δ -0.0078). F1 entrenamiento 0.7453; brecha 0.3066 (Δ -0.0523). Entrenamiento total 8.95 s (Δ -12.13 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0063, Δprecisión +0.0125, Δrecuperación +0.0125; N1: ΔF1 -0.0248, Δprecisión -0.0111, Δrecuperación -0.0228.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 30. XGBoost · Hiperparámetro · n_estimators=400

Prueba: `ajuste_XGB_pesos0_n_estimators_400`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.4466 ± 0.0320** (Δ +0.0002). F1 entrenamiento 0.8715; brecha 0.4248 (Δ +0.0659). Entrenamiento total 33.05 s (Δ +11.97 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0225, Δprecisión +0.0045, Δrecuperación +0.0212; REM: ΔF1 -0.0277, Δprecisión -0.0019, Δrecuperación -0.0418.

**Conclusión:** F1 promedio prácticamente igual en esta ronda; no hay una ventaja predictiva clara. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** Sin prioridad frente a la referencia por F1 macro.

#### 31. XGBoost · Hiperparámetro · reg_lambda=5

Prueba: `ajuste_XGB_pesos0_reg_lambda_5`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.4491 ± 0.0355** (Δ +0.0026). F1 entrenamiento 0.7998; brecha 0.3507 (Δ -0.0082). Entrenamiento total 17.08 s (Δ -4.00 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0065, Δprecisión +0.0177, Δrecuperación +0.0037; N2: ΔF1 +0.0005, Δprecisión +0.0012, Δrecuperación -0.0004.

**Conclusión:** Mayor F1 promedio en 3/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 32. XGBoost · Hiperparámetro · reg_lambda=10

Prueba: `ajuste_XGB_pesos0_reg_lambda_10`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.4460 ± 0.0330** (Δ -0.0005). F1 entrenamiento 0.7961; brecha 0.3501 (Δ -0.0088). Entrenamiento total 17.15 s (Δ -3.94 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0152, Δprecisión +0.0354, Δrecuperación +0.0115; REM: ΔF1 -0.0091, Δprecisión -0.0251, Δrecuperación +0.0015.

**Conclusión:** F1 promedio prácticamente igual en esta ronda; no hay una ventaja predictiva clara. **Decisión:** Sin prioridad frente a la referencia por F1 macro.

#### 33. XGBoost · Hiperparámetro · subsample=1.0

Prueba: `ajuste_XGB_pesos0_subsample_1.0`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.4460 ± 0.0289** (Δ -0.0005). F1 entrenamiento 0.7981; brecha 0.3521 (Δ -0.0068). Entrenamiento total 13.72 s (Δ -7.36 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0053, Δprecisión +0.0065, Δrecuperación +0.0032; REM: ΔF1 -0.0125, Δprecisión -0.0219, Δrecuperación -0.0111.

**Conclusión:** F1 promedio prácticamente igual en esta ronda; no hay una ventaja predictiva clara. **Decisión:** Sin prioridad frente a la referencia por F1 macro.

#### 34. XGBoost · Hiperparámetro · colsample_bytree=1.0

Prueba: `ajuste_XGB_pesos0_colsample_bytree_1.0`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.4413 ± 0.0311** (Δ -0.0052). F1 entrenamiento 0.8094; brecha 0.3682 (Δ +0.0092). Entrenamiento total 17.28 s (Δ -3.80 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N2: ΔF1 +0.0005, Δprecisión -0.0012, Δrecuperación +0.0025; N3: ΔF1 -0.0132, Δprecisión +0.0169, Δrecuperación -0.0142.

**Conclusión:** Menor F1 promedio; mejoró en 3/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 35. XGBoost · Hiperparámetro · max_depth=2

Prueba: `ajuste_XGB_pesos1_max_depth_2`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.4611 ± 0.0333** (Δ -0.0248). F1 entrenamiento 0.6405; brecha 0.1793 (Δ -0.1181). Entrenamiento total 13.50 s (Δ -2.85 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0250, Δprecisión -0.0043, Δrecuperación +0.0697; N3: ΔF1 -0.0621, Δprecisión -0.1341, Δrecuperación +0.1674.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 36. XGBoost · Hiperparámetro · max_depth=6

Prueba: `ajuste_XGB_pesos1_max_depth_6`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.4803 ± 0.0344** (Δ -0.0056). F1 entrenamiento 0.8958; brecha 0.4154 (Δ +0.1180). Entrenamiento total 30.63 s (Δ +14.28 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: W: ΔF1 +0.0220, Δprecisión +0.0020, Δrecuperación +0.0533; N3: ΔF1 -0.0394, Δprecisión +0.0914, Δrecuperación -0.1788.

**Conclusión:** Menor F1 promedio; mejoró en 3/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 37. XGBoost · Hiperparámetro · min_child_weight=5

Prueba: `ajuste_XGB_pesos1_min_child_weight_5`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.4879 ± 0.0303** (Δ +0.0020). F1 entrenamiento 0.7817; brecha 0.2938 (Δ -0.0036). Entrenamiento total 17.07 s (Δ +0.71 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0084, Δprecisión +0.0058, Δrecuperación +0.0084; REM: ΔF1 -0.0024, Δprecisión -0.0006, Δrecuperación -0.0035.

**Conclusión:** Mayor F1 promedio en 2/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 38. XGBoost · Hiperparámetro · min_child_weight=15

Prueba: `ajuste_XGB_pesos1_min_child_weight_15`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.4835 ± 0.0224** (Δ -0.0024). F1 entrenamiento 0.7761; brecha 0.2926 (Δ -0.0048). Entrenamiento total 16.26 s (Δ -0.10 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: REM: ΔF1 -0.0010, Δprecisión -0.0011, Δrecuperación -0.0027; W: ΔF1 -0.0057, Δprecisión -0.0039, Δrecuperación -0.0062.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 39. XGBoost · Hiperparámetro · learning_rate=0.03

Prueba: `ajuste_XGB_pesos1_learning_rate_0.03`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.4659 ± 0.0349** (Δ -0.0200). F1 entrenamiento 0.6723; brecha 0.2064 (Δ -0.0910). Entrenamiento total 17.55 s (Δ +1.20 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0252, Δprecisión -0.0058, Δrecuperación +0.0869; N3: ΔF1 -0.0386, Δprecisión -0.1098, Δrecuperación +0.1651.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. La tasa se cambió con rondas fijas; una tasa menor podría necesitar más rondas, combinación no probada. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 40. XGBoost · Hiperparámetro · n_estimators=100

Prueba: `ajuste_XGB_pesos1_n_estimators_100`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.4727 ± 0.0350** (Δ -0.0132). F1 entrenamiento 0.7160; brecha 0.2433 (Δ -0.0541). Entrenamiento total 8.99 s (Δ -7.37 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0100, Δprecisión -0.0081, Δrecuperación +0.0422; W: ΔF1 -0.0211, Δprecisión -0.0081, Δrecuperación -0.0364.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 41. XGBoost · Hiperparámetro · n_estimators=400

Prueba: `ajuste_XGB_pesos1_n_estimators_400`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.4845 ± 0.0286** (Δ -0.0014). F1 entrenamiento 0.8502; brecha 0.3657 (Δ +0.0683). Entrenamiento total 35.45 s (Δ +19.09 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: W: ΔF1 +0.0221, Δprecisión +0.0066, Δrecuperación +0.0436; N3: ΔF1 -0.0251, Δprecisión +0.0674, Δrecuperación -0.1382.

**Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 42. XGBoost · Hiperparámetro · reg_lambda=5

Prueba: `ajuste_XGB_pesos1_reg_lambda_5`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.4907 ± 0.0327** (Δ +0.0047). F1 entrenamiento 0.7785; brecha 0.2879 (Δ -0.0095). Entrenamiento total 16.63 s (Δ +0.27 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0073, Δprecisión +0.0069, Δrecuperación +0.0078; N2: ΔF1 +0.0017, Δprecisión +0.0005, Δrecuperación +0.0025.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 43. XGBoost · Hiperparámetro · reg_lambda=10

Prueba: `ajuste_XGB_pesos1_reg_lambda_10`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.4866 ± 0.0296** (Δ +0.0007). F1 entrenamiento 0.7746; brecha 0.2880 (Δ -0.0094). Entrenamiento total 17.87 s (Δ +1.51 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0034, Δprecisión -0.0046, Δrecuperación +0.0161; W: ΔF1 -0.0036, Δprecisión -0.0041, Δrecuperación -0.0022.

**Conclusión:** Mayor F1 promedio en 3/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 44. XGBoost · Hiperparámetro · subsample=1.0

Prueba: `ajuste_XGB_pesos1_subsample_1.0`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.4857 ± 0.0261** (Δ -0.0002). F1 entrenamiento 0.7774; brecha 0.2917 (Δ -0.0057). Entrenamiento total 13.76 s (Δ -2.59 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0103, Δprecisión +0.0039, Δrecuperación +0.0137; W: ΔF1 -0.0040, Δprecisión -0.0036, Δrecuperación -0.0032.

**Conclusión:** F1 promedio prácticamente igual en esta ronda; no hay una ventaja predictiva clara. **Decisión:** Sin prioridad frente a la referencia por F1 macro.

#### 45. XGBoost · Hiperparámetro · colsample_bytree=1.0

Prueba: `ajuste_XGB_pesos1_colsample_bytree_1.0`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.4885 ± 0.0243** (Δ +0.0026). F1 entrenamiento 0.7864; brecha 0.2979 (Δ +0.0005). Entrenamiento total 19.28 s (Δ +2.92 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0122, Δprecisión +0.0047, Δrecuperación +0.0183; W: ΔF1 -0.0036, Δprecisión -0.0035, Δrecuperación -0.0048.

**Conclusión:** Mayor F1 promedio en 3/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 46. Random Forest · Control · candidata

Prueba: `representacion_RF_candidata`. Referencia: `ajuste_RF_pesos1_min_samples_leaf_10`. Con pesos.

F1 macro **0.4614 → 0.4614 ± 0.0205** (Δ +0.0000). F1 entrenamiento 0.8375; brecha 0.3761 (Δ +0.0000). Entrenamiento total 31.87 s (Δ +20.65 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000; W: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000.

**Conclusión:** Repetición de la misma configuración y entradas; las diferencias de tiempo no son efecto de un hiperparámetro. **Decisión:** Usar como control de representación; no contar como mejora nueva.

#### 47. Random Forest · Representación · sin_log_combinada

Prueba: `representacion_RF_sin_log_combinada`. Referencia: `ajuste_RF_pesos1_min_samples_leaf_10`. Con pesos.

F1 macro **0.4614 → 0.4613 ± 0.0205** (Δ -0.0001). F1 entrenamiento 0.8374; brecha 0.3761 (Δ +0.0001). Entrenamiento total 30.27 s (Δ +19.05 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: N2: ΔF1 -0.0000, Δprecisión +0.0000, Δrecuperación -0.0000; N3: ΔF1 -0.0002, Δprecisión -0.0002, Δrecuperación +0.0000.

**Conclusión:** F1 promedio prácticamente igual en esta ronda; no hay una ventaja predictiva clara. **Decisión:** Sin prioridad frente a la referencia por F1 macro.

#### 48. Random Forest · Representación · separada_con_log

Prueba: `representacion_RF_separada_con_log`. Referencia: `ajuste_RF_pesos1_min_samples_leaf_10`. Con pesos.

F1 macro **0.4614 → 0.4680 ± 0.0302** (Δ +0.0066). F1 entrenamiento 0.8411; brecha 0.3731 (Δ -0.0029). Entrenamiento total 15.03 s (Δ +3.81 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0128, Δprecisión +0.0105, Δrecuperación +0.0200; N3: ΔF1 -0.0036, Δprecisión -0.0128, Δrecuperación +0.0093.

**Conclusión:** Mayor F1 promedio en 3/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 49. XGBoost · Control · candidata

Prueba: `representacion_XGB_candidata`. Referencia: `ajuste_XGB_pesos1_reg_lambda_5`. Con pesos.

F1 macro **0.4907 → 0.4907 ± 0.0327** (Δ +0.0000). F1 entrenamiento 0.7785; brecha 0.2879 (Δ +0.0000). Entrenamiento total 7.11 s (Δ -9.52 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000; W: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000.

**Conclusión:** Repetición de la misma configuración y entradas; las diferencias de tiempo no son efecto de un hiperparámetro. **Decisión:** Usar como control de representación; no contar como mejora nueva.

#### 50. XGBoost · Representación · sin_log_combinada

Prueba: `representacion_XGB_sin_log_combinada`. Referencia: `ajuste_XGB_pesos1_reg_lambda_5`. Con pesos.

F1 macro **0.4907 → 0.4907 ± 0.0327** (Δ +0.0000). F1 entrenamiento 0.7785; brecha 0.2879 (Δ +0.0000). Entrenamiento total 17.18 s (Δ +0.55 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000; W: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000.

**Conclusión:** F1 promedio prácticamente igual en esta ronda; no hay una ventaja predictiva clara. **Decisión:** Sin prioridad frente a la referencia por F1 macro.

#### 51. XGBoost · Representación · separada_con_log

Prueba: `representacion_XGB_separada_con_log`. Referencia: `ajuste_XGB_pesos1_reg_lambda_5`. Con pesos.

F1 macro **0.4907 → 0.4814 ± 0.0307** (Δ -0.0093). F1 entrenamiento 0.7839; brecha 0.3025 (Δ +0.0147). Entrenamiento total 18.16 s (Δ +1.53 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: N2: ΔF1 +0.0016, Δprecisión +0.0010, Δrecuperación +0.0030; REM: ΔF1 -0.0178, Δprecisión -0.0034, Δrecuperación -0.0284.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 52. XGBoost · Contexto temporal · Historia 1 minutos

Prueba: `contexto_pacientes_XGB_lag_1`. Referencia: `representacion_XGB_candidata`. Con pesos.

F1 macro **0.4907 → 0.4964 ± 0.0331** (Δ +0.0058). F1 entrenamiento 0.7988; brecha 0.3023 (Δ +0.0145). Entrenamiento total 29.71 s (Δ +22.60 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0270, Δprecisión +0.0364, Δrecuperación +0.0229; N3: ΔF1 -0.0139, Δprecisión -0.0096, Δrecuperación -0.0198.

**Conclusión:** Mayor F1 promedio en 3/5 folds; la brecha no se redujo claramente. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 53. XGBoost · Contexto temporal · Historia 2 minutos

Prueba: `contexto_pacientes_XGB_lag_2`. Referencia: `representacion_XGB_candidata`. Con pesos.

F1 macro **0.4907 → 0.4940 ± 0.0330** (Δ +0.0033). F1 entrenamiento 0.7965; brecha 0.3025 (Δ +0.0147). Entrenamiento total 28.28 s (Δ +21.16 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0154, Δprecisión +0.0221, Δrecuperación +0.0084; N3: ΔF1 -0.0095, Δprecisión -0.0030, Δrecuperación -0.0167.

**Conclusión:** Mayor F1 promedio en 3/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 54. XGBoost · Contexto temporal · Historia 5 minutos

Prueba: `contexto_pacientes_XGB_lag_5`. Referencia: `representacion_XGB_candidata`. Con pesos.

F1 macro **0.4907 → 0.4881 ± 0.0352** (Δ -0.0026). F1 entrenamiento 0.7934; brecha 0.3053 (Δ +0.0174). Entrenamiento total 28.61 s (Δ +21.49 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0078, Δprecisión +0.0097, Δrecuperación +0.0063; N3: ΔF1 -0.0276, Δprecisión -0.0186, Δrecuperación -0.0400.

**Conclusión:** Menor F1 promedio; mejoró en 3/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 55. XGBoost · Contexto temporal · Historia 10 minutos

Prueba: `contexto_pacientes_XGB_lag_10`. Referencia: `representacion_XGB_candidata`. Con pesos.

F1 macro **0.4907 → 0.4916 ± 0.0279** (Δ +0.0009). F1 entrenamiento 0.7925; brecha 0.3008 (Δ +0.0130). Entrenamiento total 28.04 s (Δ +20.93 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0066, Δprecisión +0.0096, Δrecuperación +0.0049; N2: ΔF1 -0.0032, Δprecisión -0.0027, Δrecuperación -0.0020.

**Conclusión:** Mayor F1 promedio en 3/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 56. XGBoost · Contexto temporal · Historia 15 minutos

Prueba: `contexto_pacientes_XGB_lag_15`. Referencia: `representacion_XGB_candidata`. Con pesos.

F1 macro **0.4907 → 0.4927 ± 0.0329** (Δ +0.0021). F1 entrenamiento 0.7920; brecha 0.2993 (Δ +0.0114). Entrenamiento total 28.21 s (Δ +21.10 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0196, Δprecisión +0.0324, Δrecuperación +0.0129; N3: ΔF1 -0.0103, Δprecisión +0.0015, Δrecuperación -0.0239.

**Conclusión:** Mayor F1 promedio en 4/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 57. XGBoost · Contexto temporal · Historia 5+10 minutos

Prueba: `contexto_pacientes_XGB_lag_5+10`. Referencia: `representacion_XGB_candidata`. Con pesos.

F1 macro **0.4907 → 0.4893 ± 0.0371** (Δ -0.0014). F1 entrenamiento 0.8002; brecha 0.3110 (Δ +0.0231). Entrenamiento total 40.22 s (Δ +33.11 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0205, Δprecisión +0.0389, Δrecuperación +0.0170; N3: ΔF1 -0.0311, Δprecisión -0.0176, Δrecuperación -0.0498.

**Conclusión:** Menor F1 promedio; mejoró en 3/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 58. XGBoost · Contexto temporal · Historia 1+2 minutos (dos mejores individuales)

Prueba: `contexto_pacientes_XGB_lag_1+2`. Referencia: `representacion_XGB_candidata`. Con pesos.

F1 macro **0.4907 → 0.5053 ± 0.0265** (Δ +0.0147). F1 entrenamiento 0.8063; brecha 0.3010 (Δ +0.0131). Entrenamiento total 42.01 s (Δ +34.89 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0377, Δprecisión +0.0295, Δrecuperación +0.0464; N3: ΔF1 +0.0002, Δprecisión +0.0131, Δrecuperación -0.0132.

**Conclusión:** Mayor F1 promedio en 4/5 folds; la brecha no se redujo claramente. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 59. XGBoost · Balanceo control · Misma configuración sin ponderación

Prueba: `balanceo_pacientes_XGB_sin_pesos`. Referencia: `representacion_XGB_candidata`. Sin pesos.

F1 macro **0.4907 → 0.4491 ± 0.0355** (Δ -0.0416). F1 entrenamiento 0.7998; brecha 0.3507 (Δ +0.0628). Entrenamiento total 17.84 s (Δ +10.72 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: N2: ΔF1 +0.0443, Δprecisión -0.0904, Δrecuperación +0.1710; N3: ΔF1 -0.1444, Δprecisión +0.1251, Δrecuperación -0.3380.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 60. XGBoost · Balanceo control · Misma configuración con pesos balanceados

Prueba: `balanceo_pacientes_XGB_pesos`. Referencia: `balanceo_pacientes_XGB_sin_pesos`. Con pesos.

F1 macro **0.4491 → 0.4907 ± 0.0327** (Δ +0.0416). F1 entrenamiento 0.7785; brecha 0.2879 (Δ -0.0628). Entrenamiento total 17.76 s (Δ -0.08 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1444, Δprecisión -0.1251, Δrecuperación +0.3380; N2: ΔF1 -0.0443, Δprecisión +0.0904, Δrecuperación -0.1710.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 61. XGBoost · Balanceo control · Escalado sin remuestreo ni pesos

Prueba: `balanceo_pacientes_XGB_escala`. Referencia: `balanceo_pacientes_XGB_sin_pesos`. Sin pesos.

F1 macro **0.4491 → 0.4451 ± 0.0332** (Δ -0.0040). F1 entrenamiento 0.7996; brecha 0.3545 (Δ +0.0038). Entrenamiento total 17.71 s (Δ -0.13 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0020, Δprecisión -0.0029, Δrecuperación +0.0027; N3: ΔF1 -0.0095, Δprecisión -0.0135, Δrecuperación -0.0090.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 62. XGBoost · SMOTE · SMOTE objetivo 50% de mayoritaria; k=3

Prueba: `smote_pacientes_XGB_ratio0.5_k3`. Referencia: `balanceo_pacientes_XGB_escala`. Sin pesos.

F1 macro **0.4451 → 0.4830 ± 0.0289** (Δ +0.0379). F1 entrenamiento 0.7976; brecha 0.3147 (Δ -0.0399). Entrenamiento total 27.19 s (Δ +9.48 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1351, Δprecisión -0.0666, Δrecuperación +0.2413; W: ΔF1 -0.0312, Δprecisión -0.0047, Δrecuperación -0.0552.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

Contra el ganador base `representacion_XGB_candidata` (F1 0.4907), ΔF1 -0.0077. No desplaza al ganador base por F1 medio, aunque mejore contra el control sin pesos.

#### 63. XGBoost · SMOTE · SMOTE objetivo 50% de mayoritaria; k=5

Prueba: `smote_pacientes_XGB_ratio0.5_k5`. Referencia: `balanceo_pacientes_XGB_escala`. Sin pesos.

F1 macro **0.4451 → 0.4818 ± 0.0210** (Δ +0.0367). F1 entrenamiento 0.7966; brecha 0.3148 (Δ -0.0397). Entrenamiento total 27.29 s (Δ +9.58 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1428, Δprecisión -0.0607, Δrecuperación +0.2436; W: ΔF1 -0.0364, Δprecisión -0.0106, Δrecuperación -0.0550.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

Contra el ganador base `representacion_XGB_candidata` (F1 0.4907), ΔF1 -0.0088. No desplaza al ganador base por F1 medio, aunque mejore contra el control sin pesos.

#### 64. XGBoost · SMOTE · SMOTE objetivo 100% de mayoritaria; k=3

Prueba: `smote_pacientes_XGB_ratio1.0_k3`. Referencia: `balanceo_pacientes_XGB_escala`. Sin pesos.

F1 macro **0.4451 → 0.4860 ± 0.0225** (Δ +0.0409). F1 entrenamiento 0.7771; brecha 0.2911 (Δ -0.0635). Entrenamiento total 42.15 s (Δ +24.44 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1501, Δprecisión -0.1005, Δrecuperación +0.3182; N2: ΔF1 -0.0424, Δprecisión +0.0856, Δrecuperación -0.1656.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

Contra el ganador base `representacion_XGB_candidata` (F1 0.4907), ΔF1 -0.0046. No desplaza al ganador base por F1 medio, aunque mejore contra el control sin pesos.

#### 65. XGBoost · SMOTE · SMOTE objetivo 100% de mayoritaria; k=5

Prueba: `smote_pacientes_XGB_ratio1.0_k5`. Referencia: `balanceo_pacientes_XGB_escala`. Sin pesos.

F1 macro **0.4451 → 0.4806 ± 0.0218** (Δ +0.0355). F1 entrenamiento 0.7732; brecha 0.2926 (Δ -0.0620). Entrenamiento total 12.59 s (Δ -5.12 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1414, Δprecisión -0.1133, Δrecuperación +0.3033; N2: ΔF1 -0.0454, Δprecisión +0.0823, Δrecuperación -0.1683.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

Contra el ganador base `representacion_XGB_candidata` (F1 0.4907), ΔF1 -0.0101. No desplaza al ganador base por F1 medio, aunque mejore contra el control sin pesos.

### Epochs mezclados: diagnóstico

Referencia trivial: F1 macro 0.1371; exactitud 0.5212. No distingue todas las etapas.

#### 01. Regresión logística · Pesos · Sin pesos → pesos balanceados

Prueba: `epochs_Logistica_pesos1`. Referencia: `epochs_Logistica_pesos0`. Con pesos.

F1 macro **0.2816 → 0.4061 ± 0.0026** (Δ +0.1245). F1 entrenamiento 0.4081; brecha 0.0021 (Δ +0.0013). Entrenamiento total 2.00 s (Δ -1.08 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.3633, Δprecisión +0.0021, Δrecuperación +0.7262; N2: ΔF1 -0.1869, Δprecisión +0.2653, Δrecuperación -0.5533.

**Conclusión:** Mayor F1 promedio en 5/5 folds; la brecha no se redujo claramente. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 02. Random Forest · Pesos · Sin pesos → pesos balanceados

Prueba: `epochs_RF_pesos1`. Referencia: `epochs_RF_pesos0`. Con pesos.

F1 macro **0.7617 → 0.7860 ± 0.0081** (Δ +0.0243). F1 entrenamiento 0.9604; brecha 0.1745 (Δ -0.0531). Entrenamiento total 8.31 s (Δ -30.17 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.1127, Δprecisión -0.1419, Δrecuperación +0.2509; N3: ΔF1 -0.0100, Δprecisión -0.1657, Δrecuperación +0.1419.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 03. XGBoost · Pesos · Sin pesos → pesos balanceados

Prueba: `epochs_XGB_pesos1`. Referencia: `epochs_XGB_pesos0`. Con pesos.

F1 macro **0.7418 → 0.7273 ± 0.0052** (Δ -0.0145). F1 entrenamiento 0.7714; brecha 0.0441 (Δ -0.0069). Entrenamiento total 5.60 s (Δ +0.63 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0832, Δprecisión -0.1617, Δrecuperación +0.2937; N3: ΔF1 -0.1014, Δprecisión -0.2923, Δrecuperación +0.1753.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 04. Referencia trivial · Protocolo · Pacientes separados → Epochs mezclados

Prueba: `epochs_Baseline_pesos0`. Referencia: `pacientes_Baseline_pesos0`. Sin pesos.

F1 macro **0.1368 → 0.1371 ± 0.0000** (Δ +0.0003). F1 entrenamiento 0.1371; brecha 0.0000 (Δ -0.0003). Entrenamiento total 0.03 s (Δ -0.06 s).

Etapas con cambios extremos: N2: ΔF1 +0.0014, Δprecisión +0.0011, Δrecuperación +0.0000; W: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 05. Regresión logística · Protocolo · Pacientes separados → Epochs mezclados

Prueba: `epochs_Logistica_pesos0`. Referencia: `pacientes_Logistica_pesos0`. Sin pesos.

F1 macro **0.2610 → 0.2816 ± 0.0053** (Δ +0.0206). F1 entrenamiento 0.2824; brecha 0.0008 (Δ -0.0367). Entrenamiento total 3.08 s (Δ +0.14 s).

Etapas con cambios extremos: N3: ΔF1 +0.0406, Δprecisión +0.2226, Δrecuperación +0.0211; REM: ΔF1 -0.0035, Δprecisión +0.0772, Δrecuperación -0.0061.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 06. Regresión logística · Protocolo · Pacientes separados → Epochs mezclados

Prueba: `epochs_Logistica_pesos1`. Referencia: `pacientes_Logistica_pesos1`. Con pesos.

F1 macro **0.3467 → 0.4061 ± 0.0026** (Δ +0.0594). F1 entrenamiento 0.4081; brecha 0.0021 (Δ -0.0708). Entrenamiento total 2.00 s (Δ -0.33 s).

Etapas con cambios extremos: N1: ΔF1 +0.0842, Δprecisión +0.0593, Δrecuperación +0.0884; REM: ΔF1 +0.0275, Δprecisión +0.0069, Δrecuperación +0.0801.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 07. Random Forest · Protocolo · Pacientes separados → Epochs mezclados

Prueba: `epochs_RF_pesos0`. Referencia: `pacientes_RF_pesos0`. Sin pesos.

F1 macro **0.3847 → 0.7617 ± 0.0083** (Δ +0.3770). F1 entrenamiento 0.9893; brecha 0.2276 (Δ -0.3771). Entrenamiento total 38.48 s (Δ -7.21 s).

Etapas con cambios extremos: N3: ΔF1 +0.6578, Δprecisión +0.1192, Δrecuperación +0.6555; N2: ΔF1 +0.0946, Δprecisión +0.1137, Δrecuperación +0.0663.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 08. Random Forest · Protocolo · Pacientes separados → Epochs mezclados

Prueba: `epochs_RF_pesos1`. Referencia: `pacientes_RF_pesos1`. Con pesos.

F1 macro **0.4412 → 0.7860 ± 0.0081** (Δ +0.3447). F1 entrenamiento 0.9604; brecha 0.1745 (Δ -0.3446). Entrenamiento total 8.31 s (Δ -28.89 s).

Etapas con cambios extremos: REM: ΔF1 +0.5335, Δprecisión +0.4968, Δrecuperación +0.5538; N2: ΔF1 +0.1121, Δprecisión +0.1218, Δrecuperación +0.1022.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 09. XGBoost · Protocolo · Pacientes separados → Epochs mezclados

Prueba: `epochs_XGB_pesos0`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.7418 ± 0.0077** (Δ +0.2954). F1 entrenamiento 0.7928; brecha 0.0510 (Δ -0.3080). Entrenamiento total 4.97 s (Δ -16.11 s).

Etapas con cambios extremos: N3: ΔF1 +0.4717, Δprecisión +0.3049, Δrecuperación +0.5092; N2: ΔF1 +0.0726, Δprecisión +0.0772, Δrecuperación +0.0654.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 10. XGBoost · Protocolo · Pacientes separados → Epochs mezclados

Prueba: `epochs_XGB_pesos1`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.7273 ± 0.0052** (Δ +0.2414). F1 entrenamiento 0.7714; brecha 0.0441 (Δ -0.2533). Entrenamiento total 5.60 s (Δ -10.76 s).

Etapas con cambios extremos: REM: ΔF1 +0.3791, Δprecisión +0.3271, Δrecuperación +0.4023; N2: ΔF1 +0.0741, Δprecisión +0.0771, Δrecuperación +0.0699.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

### Pacientes conocidos: lecturas futuras

Referencia trivial: F1 macro 0.1360; exactitud 0.5155. No distingue todas las etapas.

#### 01. Regresión logística · Pesos · Sin pesos → pesos balanceados

Prueba: `temporal_Logistica_pesos1`. Referencia: `temporal_Logistica_pesos0`. Con pesos.

F1 macro **0.2797 → 0.3683 ± 0.0343** (Δ +0.0886). F1 entrenamiento 0.4586; brecha 0.0903 (Δ -0.0158). Entrenamiento total 0.78 s (Δ -0.20 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.3216, Δprecisión +0.0822, Δrecuperación +0.5371; N2: ΔF1 -0.1736, Δprecisión +0.2126, Δrecuperación -0.5140.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 02. Random Forest · Pesos · Sin pesos → pesos balanceados

Prueba: `temporal_RF_pesos1`. Referencia: `temporal_RF_pesos0`. Con pesos.

F1 macro **0.4822 → 0.5424 ± 0.0681** (Δ +0.0602). F1 entrenamiento 0.9578; brecha 0.4154 (Δ -0.0919). Entrenamiento total 5.17 s (Δ -1.28 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1605, Δprecisión -0.1001, Δrecuperación +0.3810; N2: ΔF1 -0.0134, Δprecisión +0.0837, Δrecuperación -0.1292.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 03. XGBoost · Pesos · Sin pesos → pesos balanceados

Prueba: `temporal_XGB_pesos1`. Referencia: `temporal_XGB_pesos0`. Con pesos.

F1 macro **0.5133 → 0.5452 ± 0.0448** (Δ +0.0319). F1 entrenamiento 0.8404; brecha 0.2952 (Δ -0.0589). Entrenamiento total 4.00 s (Δ -0.25 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0789, Δprecisión -0.0358, Δrecuperación +0.2192; N2: ΔF1 -0.0285, Δprecisión +0.0875, Δrecuperación -0.1517.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 04. Referencia trivial · Protocolo · Pacientes separados → Pacientes conocidos · futuro cronológico

Prueba: `temporal_Baseline_pesos0`. Referencia: `pacientes_Baseline_pesos0`. Sin pesos.

F1 macro **0.1368 → 0.1360 ± 0.0059** (Δ -0.0008). F1 entrenamiento 0.1407; brecha 0.0047 (Δ +0.0045). Entrenamiento total 0.01 s (Δ -0.08 s).

Etapas con cambios extremos: REM: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000; N2: ΔF1 -0.0041, Δprecisión -0.0047, Δrecuperación +0.0000.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 05. Regresión logística · Protocolo · Pacientes separados → Pacientes conocidos · futuro cronológico

Prueba: `temporal_Logistica_pesos0`. Referencia: `pacientes_Logistica_pesos0`. Sin pesos.

F1 macro **0.2610 → 0.2797 ± 0.0320** (Δ +0.0187). F1 entrenamiento 0.3858; brecha 0.1061 (Δ +0.0686). Entrenamiento total 0.98 s (Δ -1.95 s).

Etapas con cambios extremos: N1: ΔF1 +0.0555, Δprecisión +0.2650, Δrecuperación +0.0324; REM: ΔF1 -0.0202, Δprecisión +0.0010, Δrecuperación -0.0151.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 06. Regresión logística · Protocolo · Pacientes separados → Pacientes conocidos · futuro cronológico

Prueba: `temporal_Logistica_pesos1`. Referencia: `pacientes_Logistica_pesos1`. Con pesos.

F1 macro **0.3467 → 0.3683 ± 0.0343** (Δ +0.0216). F1 entrenamiento 0.4586; brecha 0.0903 (Δ +0.0174). Entrenamiento total 0.78 s (Δ -1.55 s).

Etapas con cambios extremos: N1: ΔF1 +0.0754, Δprecisión +0.0293, Δrecuperación +0.1200; N3: ΔF1 -0.0488, Δprecisión -0.0369, Δrecuperación +0.1700.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 07. Random Forest · Protocolo · Pacientes separados → Pacientes conocidos · futuro cronológico

Prueba: `temporal_RF_pesos0`. Referencia: `pacientes_RF_pesos0`. Sin pesos.

F1 macro **0.3847 → 0.4822 ± 0.0591** (Δ +0.0975). F1 entrenamiento 0.9894; brecha 0.5073 (Δ -0.0974). Entrenamiento total 6.45 s (Δ -39.24 s).

Etapas con cambios extremos: N3: ΔF1 +0.2375, Δprecisión -0.2090, Δrecuperación +0.2244; REM: ΔF1 -0.0657, Δprecisión +0.1620, Δrecuperación -0.1130.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 08. Random Forest · Protocolo · Pacientes separados → Pacientes conocidos · futuro cronológico

Prueba: `temporal_RF_pesos1`. Referencia: `pacientes_RF_pesos1`. Con pesos.

F1 macro **0.4412 → 0.5424 ± 0.0681** (Δ +0.1012). F1 entrenamiento 0.9578; brecha 0.4154 (Δ -0.1036). Entrenamiento total 5.17 s (Δ -32.03 s).

Etapas con cambios extremos: N3: ΔF1 +0.1640, Δprecisión -0.0487, Δrecuperación +0.3691; REM: ΔF1 +0.0040, Δprecisión +0.1384, Δrecuperación -0.0715.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 09. XGBoost · Protocolo · Pacientes separados → Pacientes conocidos · futuro cronológico

Prueba: `temporal_XGB_pesos0`. Referencia: `pacientes_XGB_pesos0`. Sin pesos.

F1 macro **0.4465 → 0.5133 ± 0.0604** (Δ +0.0668). F1 entrenamiento 0.8674; brecha 0.3541 (Δ -0.0048). Entrenamiento total 4.25 s (Δ -16.83 s).

Etapas con cambios extremos: N1: ΔF1 +0.1614, Δprecisión +0.1082, Δrecuperación +0.1548; REM: ΔF1 -0.0626, Δprecisión +0.1101, Δrecuperación -0.1325.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 10. XGBoost · Protocolo · Pacientes separados → Pacientes conocidos · futuro cronológico

Prueba: `temporal_XGB_pesos1`. Referencia: `pacientes_XGB_pesos1`. Con pesos.

F1 macro **0.4859 → 0.5452 ± 0.0448** (Δ +0.0592). F1 entrenamiento 0.8404; brecha 0.2952 (Δ -0.0022). Entrenamiento total 4.00 s (Δ -12.36 s).

Etapas con cambios extremos: W: ΔF1 +0.1641, Δprecisión +0.1621, Δrecuperación +0.1421; REM: ΔF1 -0.0236, Δprecisión +0.1604, Δrecuperación -0.1195.

**Conclusión:** Cambian personas, orden temporal y población evaluada; las cifras responden preguntas diferentes. **Decisión:** Interpretar cada escenario por separado; no elegir por la mayor cifra entre protocolos.

#### 11. Regresión logística · Hiperparámetro · C=0.01

Prueba: `temporal_ajuste_Logistica_pesos0_C_0.01`. Referencia: `temporal_Logistica_pesos0`. Sin pesos.

F1 macro **0.2797 → 0.2588 ± 0.0192** (Δ -0.0208). F1 entrenamiento 0.3067; brecha 0.0479 (Δ -0.0582). Entrenamiento total 1.25 s (Δ +0.27 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: W: ΔF1 +0.0008, Δprecisión +0.0074, Δrecuperación -0.0021; N3: ΔF1 -0.0592, Δprecisión -0.0662, Δrecuperación -0.0490.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 12. Regresión logística · Hiperparámetro · C=0.1

Prueba: `temporal_ajuste_Logistica_pesos0_C_0.1`. Referencia: `temporal_Logistica_pesos0`. Sin pesos.

F1 macro **0.2797 → 0.2754 ± 0.0289** (Δ -0.0042). F1 entrenamiento 0.3528; brecha 0.0773 (Δ -0.0288). Entrenamiento total 1.48 s (Δ +0.50 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: W: ΔF1 +0.0005, Δprecisión +0.0012, Δrecuperación +0.0002; N3: ΔF1 -0.0134, Δprecisión -0.0082, Δrecuperación -0.0133.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 13. Regresión logística · Hiperparámetro · C=10

Prueba: `temporal_ajuste_Logistica_pesos0_C_10`. Referencia: `temporal_Logistica_pesos0`. Sin pesos.

F1 macro **0.2797 → 0.2825 ± 0.0347** (Δ +0.0029). F1 entrenamiento 0.3958; brecha 0.1133 (Δ +0.0072). Entrenamiento total 1.98 s (Δ +1.00 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0084, Δprecisión +0.0785, Δrecuperación +0.0045; W: ΔF1 +0.0002, Δprecisión +0.0002, Δrecuperación +0.0002.

**Conclusión:** Mayor F1 promedio en 5/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 14. Regresión logística · Hiperparámetro · C=0.01

Prueba: `temporal_ajuste_Logistica_pesos1_C_0.01`. Referencia: `temporal_Logistica_pesos1`. Con pesos.

F1 macro **0.3683 → 0.3498 ± 0.0280** (Δ -0.0185). F1 entrenamiento 0.4272; brecha 0.0775 (Δ -0.0128). Entrenamiento total 0.70 s (Δ -0.08 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N1: ΔF1 -0.0044, Δprecisión -0.0018, Δrecuperación -0.0091; N2: ΔF1 -0.0530, Δprecisión -0.0182, Δrecuperación -0.0547.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 15. Regresión logística · Hiperparámetro · C=0.1

Prueba: `temporal_ajuste_Logistica_pesos1_C_0.1`. Referencia: `temporal_Logistica_pesos1`. Con pesos.

F1 macro **0.3683 → 0.3646 ± 0.0320** (Δ -0.0037). F1 entrenamiento 0.4473; brecha 0.0827 (Δ -0.0076). Entrenamiento total 1.18 s (Δ +0.40 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0004, Δprecisión -0.0113, Δrecuperación +0.0004; N2: ΔF1 -0.0112, Δprecisión -0.0022, Δrecuperación -0.0127.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 16. Regresión logística · Hiperparámetro · C=10

Prueba: `temporal_ajuste_Logistica_pesos1_C_10`. Referencia: `temporal_Logistica_pesos1`. Con pesos.

F1 macro **0.3683 → 0.3685 ± 0.0345** (Δ +0.0002). F1 entrenamiento 0.4668; brecha 0.0983 (Δ +0.0080). Entrenamiento total 1.61 s (Δ +0.83 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N2: ΔF1 +0.0012, Δprecisión +0.0009, Δrecuperación +0.0012; N3: ΔF1 -0.0006, Δprecisión -0.0004, Δrecuperación -0.0025.

**Conclusión:** F1 promedio prácticamente igual en esta ronda; no hay una ventaja predictiva clara. **Decisión:** Sin prioridad frente a la referencia por F1 macro.

#### 17. Random Forest · Hiperparámetro · max_depth=8

Prueba: `temporal_ajuste_RF_pesos0_max_depth_8`. Referencia: `temporal_RF_pesos0`. Sin pesos.

F1 macro **0.4822 → 0.3304 ± 0.0554** (Δ -0.1518). F1 entrenamiento 0.5165; brecha 0.1861 (Δ -0.3212). Entrenamiento total 11.98 s (Δ +5.54 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N2: ΔF1 -0.0773, Δprecisión -0.1333, Δrecuperación +0.0441; REM: ΔF1 -0.2799, Δprecisión -0.1872, Δrecuperación -0.1953.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 18. Random Forest · Hiperparámetro · max_depth=16

Prueba: `temporal_ajuste_RF_pesos0_max_depth_16`. Referencia: `temporal_RF_pesos0`. Sin pesos.

F1 macro **0.4822 → 0.4430 ± 0.0532** (Δ -0.0392). F1 entrenamiento 0.9147; brecha 0.4717 (Δ -0.0356). Entrenamiento total 18.98 s (Δ +12.54 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: W: ΔF1 -0.0109, Δprecisión +0.0142, Δrecuperación -0.0424; REM: ΔF1 -0.0941, Δprecisión +0.0079, Δrecuperación -0.0812.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 19. Random Forest · Hiperparámetro · min_samples_leaf=10

Prueba: `temporal_ajuste_RF_pesos0_min_samples_leaf_10`. Referencia: `temporal_RF_pesos0`. Sin pesos.

F1 macro **0.4822 → 0.4557 ± 0.0498** (Δ -0.0265). F1 entrenamiento 0.8251; brecha 0.3694 (Δ -0.1379). Entrenamiento total 20.10 s (Δ +13.66 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N3: ΔF1 -0.0003, Δprecisión +0.0570, Δrecuperación -0.0018; N1: ΔF1 -0.0473, Δprecisión +0.0028, Δrecuperación -0.0458.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 20. Random Forest · Hiperparámetro · min_samples_leaf=30

Prueba: `temporal_ajuste_RF_pesos0_min_samples_leaf_30`. Referencia: `temporal_RF_pesos0`. Sin pesos.

F1 macro **0.4822 → 0.4075 ± 0.0290** (Δ -0.0747). F1 entrenamiento 0.6606; brecha 0.2531 (Δ -0.2542). Entrenamiento total 17.21 s (Δ +10.77 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N3: ΔF1 -0.0165, Δprecisión +0.0921, Δrecuperación -0.0192; REM: ΔF1 -0.1332, Δprecisión -0.2004, Δrecuperación -0.1036.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 21. Random Forest · Hiperparámetro · max_features=0.5

Prueba: `temporal_ajuste_RF_pesos0_max_features_0.5`. Referencia: `temporal_RF_pesos0`. Sin pesos.

F1 macro **0.4822 → 0.4891 ± 0.0588** (Δ +0.0070). F1 entrenamiento 0.9913; brecha 0.5022 (Δ -0.0051). Entrenamiento total 59.28 s (Δ +52.84 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0253, Δprecisión -0.0037, Δrecuperación +0.0285; N3: ΔF1 -0.0118, Δprecisión -0.0498, Δrecuperación +0.0049.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. Cambia cuántas variables compiten por división y la diversidad de árboles. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 22. Random Forest · Hiperparámetro · n_estimators=100

Prueba: `temporal_ajuste_RF_pesos0_n_estimators_100`. Referencia: `temporal_RF_pesos0`. Sin pesos.

F1 macro **0.4822 → 0.4796 ± 0.0558** (Δ -0.0025). F1 entrenamiento 0.9891; brecha 0.5095 (Δ +0.0022). Entrenamiento total 11.49 s (Δ +5.04 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0043, Δprecisión -0.0025, Δrecuperación +0.0053; N3: ΔF1 -0.0130, Δprecisión -0.0173, Δrecuperación -0.0108.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 23. Random Forest · Hiperparámetro · n_estimators=400

Prueba: `temporal_ajuste_RF_pesos0_n_estimators_400`. Referencia: `temporal_RF_pesos0`. Sin pesos.

F1 macro **0.4822 → 0.4842 ± 0.0587** (Δ +0.0021). F1 entrenamiento 0.9901; brecha 0.5059 (Δ -0.0014). Entrenamiento total 27.08 s (Δ +20.63 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0070, Δprecisión +0.0180, Δrecuperación +0.0036; REM: ΔF1 -0.0001, Δprecisión +0.0149, Δrecuperación -0.0012.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 24. Random Forest · Hiperparámetro · max_depth=8

Prueba: `temporal_ajuste_RF_pesos1_max_depth_8`. Referencia: `temporal_RF_pesos1`. Con pesos.

F1 macro **0.5424 → 0.4468 ± 0.0341** (Δ -0.0956). F1 entrenamiento 0.6764; brecha 0.2296 (Δ -0.1859). Entrenamiento total 3.29 s (Δ -1.88 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 -0.0086, Δprecisión -0.2280, Δrecuperación +0.2074; N3: ΔF1 -0.1899, Δprecisión -0.2287, Δrecuperación +0.1238.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 25. Random Forest · Hiperparámetro · max_depth=16

Prueba: `temporal_ajuste_RF_pesos1_max_depth_16`. Referencia: `temporal_RF_pesos1`. Con pesos.

F1 macro **0.5424 → 0.5395 ± 0.0613** (Δ -0.0029). F1 entrenamiento 0.9129; brecha 0.3734 (Δ -0.0421). Entrenamiento total 4.43 s (Δ -0.74 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0216, Δprecisión -0.0627, Δrecuperación +0.0657; N2: ΔF1 -0.0222, Δprecisión +0.0104, Δrecuperación -0.0496.

**Conclusión:** Menor F1 promedio; mejoró en 3/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 26. Random Forest · Hiperparámetro · min_samples_leaf=10

Prueba: `temporal_ajuste_RF_pesos1_min_samples_leaf_10`. Referencia: `temporal_RF_pesos1`. Con pesos.

F1 macro **0.5424 → 0.5188 ± 0.0533** (Δ -0.0236). F1 entrenamiento 0.8390; brecha 0.3202 (Δ -0.0953). Entrenamiento total 4.17 s (Δ -1.00 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0422, Δprecisión -0.0665, Δrecuperación +0.0829; N3: ΔF1 -0.1030, Δprecisión -0.1544, Δrecuperación +0.1073.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 27. Random Forest · Hiperparámetro · min_samples_leaf=30

Prueba: `temporal_ajuste_RF_pesos1_min_samples_leaf_30`. Referencia: `temporal_RF_pesos1`. Con pesos.

F1 macro **0.5424 → 0.4793 ± 0.0408** (Δ -0.0631). F1 entrenamiento 0.7252; brecha 0.2459 (Δ -0.1696). Entrenamiento total 5.75 s (Δ +0.58 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0335, Δprecisión -0.1391, Δrecuperación +0.1346; N3: ΔF1 -0.1973, Δprecisión -0.2432, Δrecuperación +0.1397.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 28. Random Forest · Hiperparámetro · max_features=0.5

Prueba: `temporal_ajuste_RF_pesos1_max_features_0.5`. Referencia: `temporal_RF_pesos1`. Con pesos.

F1 macro **0.5424 → 0.5337 ± 0.0636** (Δ -0.0087). F1 entrenamiento 0.9579; brecha 0.4242 (Δ +0.0088). Entrenamiento total 11.72 s (Δ +6.55 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: N1: ΔF1 -0.0024, Δprecisión -0.0052, Δrecuperación +0.0024; N3: ΔF1 -0.0250, Δprecisión -0.0307, Δrecuperación -0.0106.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. Cambia cuántas variables compiten por división y la diversidad de árboles. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 29. Random Forest · Hiperparámetro · n_estimators=100

Prueba: `temporal_ajuste_RF_pesos1_n_estimators_100`. Referencia: `temporal_RF_pesos1`. Con pesos.

F1 macro **0.5424 → 0.5395 ± 0.0648** (Δ -0.0029). F1 entrenamiento 0.9567; brecha 0.4172 (Δ +0.0018). Entrenamiento total 2.80 s (Δ -2.37 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: W: ΔF1 -0.0006, Δprecisión +0.0010, Δrecuperación -0.0024; REM: ΔF1 -0.0049, Δprecisión -0.0076, Δrecuperación -0.0039.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 30. Random Forest · Hiperparámetro · n_estimators=400

Prueba: `temporal_ajuste_RF_pesos1_n_estimators_400`. Referencia: `temporal_RF_pesos1`. Con pesos.

F1 macro **0.5424 → 0.5459 ± 0.0674** (Δ +0.0035). F1 entrenamiento 0.9585; brecha 0.4126 (Δ -0.0028). Entrenamiento total 10.48 s (Δ +5.31 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0068, Δprecisión +0.0109, Δrecuperación -0.0082; W: ΔF1 +0.0014, Δprecisión +0.0008, Δrecuperación +0.0022.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. La ventaja media es pequeña, sin prueba de superioridad estadística. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 31. XGBoost · Hiperparámetro · max_depth=2

Prueba: `temporal_ajuste_XGB_pesos0_max_depth_2`. Referencia: `temporal_XGB_pesos0`. Sin pesos.

F1 macro **0.5133 → 0.4924 ± 0.0586** (Δ -0.0209). F1 entrenamiento 0.7325; brecha 0.2401 (Δ -0.1140). Entrenamiento total 3.17 s (Δ -1.08 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0009, Δprecisión -0.0341, Δrecuperación +0.0190; N1: ΔF1 -0.0477, Δprecisión -0.0054, Δrecuperación -0.0611.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 32. XGBoost · Hiperparámetro · max_depth=6

Prueba: `temporal_ajuste_XGB_pesos0_max_depth_6`. Referencia: `temporal_XGB_pesos0`. Sin pesos.

F1 macro **0.5133 → 0.5139 ± 0.0617** (Δ +0.0006). F1 entrenamiento 0.9630; brecha 0.4491 (Δ +0.0950). Entrenamiento total 6.58 s (Δ +2.33 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: N1: ΔF1 +0.0186, Δprecisión +0.0032, Δrecuperación +0.0270; REM: ΔF1 -0.0183, Δprecisión +0.0336, Δrecuperación -0.0189.

**Conclusión:** Mayor F1 promedio en 2/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 33. XGBoost · Hiperparámetro · min_child_weight=5

Prueba: `temporal_ajuste_XGB_pesos0_min_child_weight_5`. Referencia: `temporal_XGB_pesos0`. Sin pesos.

F1 macro **0.5133 → 0.5122 ± 0.0642** (Δ -0.0011). F1 entrenamiento 0.8590; brecha 0.3468 (Δ -0.0073). Entrenamiento total 4.16 s (Δ -0.09 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0030, Δprecisión +0.0057, Δrecuperación +0.0006; N1: ΔF1 -0.0058, Δprecisión -0.0067, Δrecuperación -0.0039.

**Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 34. XGBoost · Hiperparámetro · min_child_weight=15

Prueba: `temporal_ajuste_XGB_pesos0_min_child_weight_15`. Referencia: `temporal_XGB_pesos0`. Sin pesos.

F1 macro **0.5133 → 0.5107 ± 0.0641** (Δ -0.0025). F1 entrenamiento 0.8421; brecha 0.3313 (Δ -0.0228). Entrenamiento total 3.96 s (Δ -0.29 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0019, Δprecisión -0.0318, Δrecuperación +0.0033; N1: ΔF1 -0.0079, Δprecisión -0.0056, Δrecuperación -0.0082.

**Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 35. XGBoost · Hiperparámetro · learning_rate=0.03

Prueba: `temporal_ajuste_XGB_pesos0_learning_rate_0.03`. Referencia: `temporal_XGB_pesos0`. Sin pesos.

F1 macro **0.5133 → 0.4768 ± 0.0517** (Δ -0.0365). F1 entrenamiento 0.7644; brecha 0.2876 (Δ -0.0665). Entrenamiento total 4.35 s (Δ +0.10 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N2: ΔF1 -0.0162, Δprecisión -0.0293, Δrecuperación +0.0040; N1: ΔF1 -0.0731, Δprecisión -0.0124, Δrecuperación -0.0879.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. La tasa se cambió con rondas fijas; una tasa menor podría necesitar más rondas, combinación no probada. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 36. XGBoost · Hiperparámetro · n_estimators=100

Prueba: `temporal_ajuste_XGB_pesos0_n_estimators_100`. Referencia: `temporal_XGB_pesos0`. Sin pesos.

F1 macro **0.5133 → 0.4995 ± 0.0578** (Δ -0.0138). F1 entrenamiento 0.8068; brecha 0.3073 (Δ -0.0468). Entrenamiento total 2.03 s (Δ -2.22 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 -0.0039, Δprecisión -0.0288, Δrecuperación -0.0012; N1: ΔF1 -0.0219, Δprecisión +0.0050, Δrecuperación -0.0325.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 37. XGBoost · Hiperparámetro · n_estimators=400

Prueba: `temporal_ajuste_XGB_pesos0_n_estimators_400`. Referencia: `temporal_XGB_pesos0`. Sin pesos.

F1 macro **0.5133 → 0.5211 ± 0.0603** (Δ +0.0078). F1 entrenamiento 0.9277; brecha 0.4066 (Δ +0.0525). Entrenamiento total 8.15 s (Δ +3.90 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0183, Δprecisión +0.0388, Δrecuperación +0.0115; REM: ΔF1 -0.0081, Δprecisión +0.0059, Δrecuperación -0.0085.

**Conclusión:** Mayor F1 promedio en 5/5 folds; la brecha no se redujo claramente. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 38. XGBoost · Hiperparámetro · reg_lambda=5

Prueba: `temporal_ajuste_XGB_pesos0_reg_lambda_5`. Referencia: `temporal_XGB_pesos0`. Sin pesos.

F1 macro **0.5133 → 0.5113 ± 0.0597** (Δ -0.0020). F1 entrenamiento 0.8584; brecha 0.3471 (Δ -0.0070). Entrenamiento total 4.18 s (Δ -0.07 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0038, Δprecisión +0.0030, Δrecuperación +0.0010; N1: ΔF1 -0.0084, Δprecisión -0.0072, Δrecuperación -0.0086.

**Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 39. XGBoost · Hiperparámetro · reg_lambda=10

Prueba: `temporal_ajuste_XGB_pesos0_reg_lambda_10`. Referencia: `temporal_XGB_pesos0`. Sin pesos.

F1 macro **0.5133 → 0.5105 ± 0.0580** (Δ -0.0027). F1 entrenamiento 0.8520; brecha 0.3415 (Δ -0.0126). Entrenamiento total 4.18 s (Δ -0.07 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0043, Δprecisión +0.0179, Δrecuperación +0.0012; N1: ΔF1 -0.0118, Δprecisión -0.0075, Δrecuperación -0.0126.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 40. XGBoost · Hiperparámetro · subsample=1.0

Prueba: `temporal_ajuste_XGB_pesos0_subsample_1.0`. Referencia: `temporal_XGB_pesos0`. Sin pesos.

F1 macro **0.5133 → 0.5057 ± 0.0664** (Δ -0.0076). F1 entrenamiento 0.8579; brecha 0.3522 (Δ -0.0019). Entrenamiento total 3.90 s (Δ -0.35 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: W: ΔF1 -0.0019, Δprecisión -0.0018, Δrecuperación -0.0016; N1: ΔF1 -0.0130, Δprecisión -0.0057, Δrecuperación -0.0158.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 41. XGBoost · Hiperparámetro · colsample_bytree=1.0

Prueba: `temporal_ajuste_XGB_pesos0_colsample_bytree_1.0`. Referencia: `temporal_XGB_pesos0`. Sin pesos.

F1 macro **0.5133 → 0.5125 ± 0.0644** (Δ -0.0007). F1 entrenamiento 0.8696; brecha 0.3570 (Δ +0.0029). Entrenamiento total 12.43 s (Δ +8.18 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0015, Δprecisión +0.0054, Δrecuperación +0.0038; REM: ΔF1 -0.0032, Δprecisión -0.0119, Δrecuperación -0.0013.

**Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 42. XGBoost · Hiperparámetro · max_depth=2

Prueba: `temporal_ajuste_XGB_pesos1_max_depth_2`. Referencia: `temporal_XGB_pesos1`. Con pesos.

F1 macro **0.5452 → 0.4964 ± 0.0301** (Δ -0.0487). F1 entrenamiento 0.6975; brecha 0.2011 (Δ -0.0942). Entrenamiento total 8.13 s (Δ +4.13 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0199, Δprecisión -0.1964, Δrecuperación +0.1215; N3: ΔF1 -0.1322, Δprecisión -0.1327, Δrecuperación +0.0837.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 43. XGBoost · Hiperparámetro · max_depth=6

Prueba: `temporal_ajuste_XGB_pesos1_max_depth_6`. Referencia: `temporal_XGB_pesos1`. Con pesos.

F1 macro **0.5452 → 0.5567 ± 0.0522** (Δ +0.0115). F1 entrenamiento 0.9394; brecha 0.3827 (Δ +0.0875). Entrenamiento total 20.29 s (Δ +16.29 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0406, Δprecisión +0.0876, Δrecuperación -0.1271; REM: ΔF1 -0.0192, Δprecisión +0.1701, Δrecuperación -0.0482.

**Conclusión:** Mayor F1 promedio en 3/5 folds; la brecha no se redujo claramente. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 44. XGBoost · Hiperparámetro · min_child_weight=5

Prueba: `temporal_ajuste_XGB_pesos1_min_child_weight_5`. Referencia: `temporal_XGB_pesos1`. Con pesos.

F1 macro **0.5452 → 0.5435 ± 0.0402** (Δ -0.0016). F1 entrenamiento 0.8330; brecha 0.2895 (Δ -0.0057). Entrenamiento total 16.21 s (Δ +12.21 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0097, Δprecisión -0.1050, Δrecuperación +0.0147; N3: ΔF1 -0.0114, Δprecisión -0.0122, Δrecuperación +0.0019.

**Conclusión:** Menor F1 promedio; mejoró en 3/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 45. XGBoost · Hiperparámetro · min_child_weight=15

Prueba: `temporal_ajuste_XGB_pesos1_min_child_weight_15`. Referencia: `temporal_XGB_pesos1`. Con pesos.

F1 macro **0.5452 → 0.5425 ± 0.0433** (Δ -0.0026). F1 entrenamiento 0.8209; brecha 0.2784 (Δ -0.0168). Entrenamiento total 12.05 s (Δ +8.06 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0062, Δprecisión -0.1128, Δrecuperación +0.0128; N2: ΔF1 -0.0069, Δprecisión +0.0017, Δrecuperación -0.0144.

**Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 46. XGBoost · Hiperparámetro · learning_rate=0.03

Prueba: `temporal_ajuste_XGB_pesos1_learning_rate_0.03`. Referencia: `temporal_XGB_pesos1`. Con pesos.

F1 macro **0.5452 → 0.5034 ± 0.0337** (Δ -0.0417). F1 entrenamiento 0.7294; brecha 0.2259 (Δ -0.0693). Entrenamiento total 13.35 s (Δ +9.35 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0252, Δprecisión -0.1170, Δrecuperación +0.1127; N3: ΔF1 -0.1222, Δprecisión -0.1254, Δrecuperación +0.0951.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. La tasa se cambió con rondas fijas; una tasa menor podría necesitar más rondas, combinación no probada. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 47. XGBoost · Hiperparámetro · n_estimators=100

Prueba: `temporal_ajuste_XGB_pesos1_n_estimators_100`. Referencia: `temporal_XGB_pesos1`. Con pesos.

F1 macro **0.5452 → 0.5215 ± 0.0341** (Δ -0.0236). F1 entrenamiento 0.7754; brecha 0.2539 (Δ -0.0413). Entrenamiento total 6.67 s (Δ +2.68 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0130, Δprecisión -0.0917, Δrecuperación +0.0565; N3: ΔF1 -0.0766, Δprecisión -0.0830, Δrecuperación +0.0759.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. La menor brecha no compensó la pérdida de validación. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 48. XGBoost · Hiperparámetro · n_estimators=400

Prueba: `temporal_ajuste_XGB_pesos1_n_estimators_400`. Referencia: `temporal_XGB_pesos1`. Con pesos.

F1 macro **0.5452 → 0.5516 ± 0.0553** (Δ +0.0064). F1 entrenamiento 0.9038; brecha 0.3522 (Δ +0.0570). Entrenamiento total 30.73 s (Δ +26.73 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0331, Δprecisión +0.0689, Δrecuperación -0.1075; REM: ΔF1 -0.0212, Δprecisión -0.0571, Δrecuperación -0.0414.

**Conclusión:** Mayor F1 promedio en 4/5 folds; la brecha no se redujo claramente. Más árboles/rondas no garantiza mejor validación; revisar el costo medido. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 49. XGBoost · Hiperparámetro · reg_lambda=5

Prueba: `temporal_ajuste_XGB_pesos1_reg_lambda_5`. Referencia: `temporal_XGB_pesos1`. Con pesos.

F1 macro **0.5452 → 0.5427 ± 0.0417** (Δ -0.0025). F1 entrenamiento 0.8326; brecha 0.2899 (Δ -0.0053). Entrenamiento total 12.19 s (Δ +8.20 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0040, Δprecisión -0.1102, Δrecuperación +0.0095; N1: ΔF1 -0.0062, Δprecisión -0.0062, Δrecuperación -0.0059.

**Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 50. XGBoost · Hiperparámetro · reg_lambda=10

Prueba: `temporal_ajuste_XGB_pesos1_reg_lambda_10`. Referencia: `temporal_XGB_pesos1`. Con pesos.

F1 macro **0.5452 → 0.5437 ± 0.0415** (Δ -0.0015). F1 entrenamiento 0.8264; brecha 0.2827 (Δ -0.0125). Entrenamiento total 12.45 s (Δ +8.45 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0063, Δprecisión -0.1130, Δrecuperación +0.0141; N3: ΔF1 -0.0086, Δprecisión -0.0115, Δrecuperación +0.0071.

**Conclusión:** Menor F1 promedio; mejoró en 3/5 folds. La menor brecha no compensó la pérdida de validación. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 51. XGBoost · Hiperparámetro · subsample=1.0

Prueba: `temporal_ajuste_XGB_pesos1_subsample_1.0`. Referencia: `temporal_XGB_pesos1`. Con pesos.

F1 macro **0.5452 → 0.5331 ± 0.0445** (Δ -0.0121). F1 entrenamiento 0.8325; brecha 0.2994 (Δ +0.0042). Entrenamiento total 10.40 s (Δ +6.40 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: N3: ΔF1 -0.0027, Δprecisión -0.0082, Δrecuperación +0.0237; REM: ΔF1 -0.0198, Δprecisión -0.1252, Δrecuperación -0.0161.

**Conclusión:** Menor F1 promedio; mejoró en 0/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 52. XGBoost · Hiperparámetro · colsample_bytree=1.0

Prueba: `temporal_ajuste_XGB_pesos1_colsample_bytree_1.0`. Referencia: `temporal_XGB_pesos1`. Con pesos.

F1 macro **0.5452 → 0.5439 ± 0.0434** (Δ -0.0012). F1 entrenamiento 0.8426; brecha 0.2987 (Δ +0.0035). Entrenamiento total 12.63 s (Δ +8.63 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0035, Δprecisión -0.1029, Δrecuperación +0.0060; N1: ΔF1 -0.0069, Δprecisión -0.0056, Δrecuperación -0.0103.

**Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 53. Random Forest · Control · candidata

Prueba: `temporal_representacion_RF_candidata`. Referencia: `temporal_ajuste_RF_pesos1_n_estimators_400`. Con pesos.

F1 macro **0.5459 → 0.5459 ± 0.0674** (Δ +0.0000). F1 entrenamiento 0.9585; brecha 0.4126 (Δ +0.0000). Entrenamiento total 35.05 s (Δ +24.57 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000; W: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000.

**Conclusión:** Repetición de la misma configuración y entradas; las diferencias de tiempo no son efecto de un hiperparámetro. **Decisión:** Usar como control de representación; no contar como mejora nueva.

#### 54. Random Forest · Representación · sin_log_combinada

Prueba: `temporal_representacion_RF_sin_log_combinada`. Referencia: `temporal_ajuste_RF_pesos1_n_estimators_400`. Con pesos.

F1 macro **0.5459 → 0.5462 ± 0.0673** (Δ +0.0002). F1 entrenamiento 0.9584; brecha 0.4123 (Δ -0.0003). Entrenamiento total 34.78 s (Δ +24.30 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0006, Δprecisión +0.0006, Δrecuperación +0.0005; N1: ΔF1 +0.0000, Δprecisión -0.0000, Δrecuperación +0.0000.

**Conclusión:** F1 promedio prácticamente igual en esta ronda; no hay una ventaja predictiva clara. **Decisión:** Sin prioridad frente a la referencia por F1 macro.

#### 55. Random Forest · Representación · separada_con_log

Prueba: `temporal_representacion_RF_separada_con_log`. Referencia: `temporal_ajuste_RF_pesos1_n_estimators_400`. Con pesos.

F1 macro **0.5459 → 0.5526 ± 0.0730** (Δ +0.0066). F1 entrenamiento 0.9578; brecha 0.4052 (Δ -0.0074). Entrenamiento total 43.23 s (Δ +32.75 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0134, Δprecisión +0.0008, Δrecuperación +0.0140; N1: ΔF1 +0.0036, Δprecisión +0.0016, Δrecuperación +0.0075.

**Conclusión:** Mayor F1 promedio en 3/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 56. XGBoost · Control · candidata

Prueba: `temporal_representacion_XGB_candidata`. Referencia: `temporal_ajuste_XGB_pesos1_max_depth_6`. Con pesos.

F1 macro **0.5567 → 0.5567 ± 0.0522** (Δ +0.0000). F1 entrenamiento 0.9394; brecha 0.3827 (Δ +0.0000). Entrenamiento total 19.31 s (Δ -0.98 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000; W: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000.

**Conclusión:** Repetición de la misma configuración y entradas; las diferencias de tiempo no son efecto de un hiperparámetro. **Decisión:** Usar como control de representación; no contar como mejora nueva.

#### 57. XGBoost · Representación · sin_log_combinada

Prueba: `temporal_representacion_XGB_sin_log_combinada`. Referencia: `temporal_ajuste_XGB_pesos1_max_depth_6`. Con pesos.

F1 macro **0.5567 → 0.5567 ± 0.0522** (Δ +0.0000). F1 entrenamiento 0.9394; brecha 0.3827 (Δ +0.0000). Entrenamiento total 20.18 s (Δ -0.10 s). Mayor F1 en 0/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000; W: ΔF1 +0.0000, Δprecisión +0.0000, Δrecuperación +0.0000.

**Conclusión:** F1 promedio prácticamente igual en esta ronda; no hay una ventaja predictiva clara. **Decisión:** Sin prioridad frente a la referencia por F1 macro.

#### 58. XGBoost · Representación · separada_con_log

Prueba: `temporal_representacion_XGB_separada_con_log`. Referencia: `temporal_ajuste_XGB_pesos1_max_depth_6`. Con pesos.

F1 macro **0.5567 → 0.5457 ± 0.0536** (Δ -0.0110). F1 entrenamiento 0.9440; brecha 0.3983 (Δ +0.0156). Entrenamiento total 20.56 s (Δ +0.27 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: N2: ΔF1 +0.0048, Δprecisión -0.0003, Δrecuperación +0.0096; N3: ΔF1 -0.0578, Δprecisión -0.0428, Δrecuperación -0.0861.

**Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 59. XGBoost · Contexto temporal · Historia 1 minutos

Prueba: `contexto_temporal_XGB_lag_1`. Referencia: `temporal_representacion_XGB_candidata`. Con pesos.

F1 macro **0.5567 → 0.5601 ± 0.0556** (Δ +0.0034). F1 entrenamiento 0.9535; brecha 0.3934 (Δ +0.0107). Entrenamiento total 31.93 s (Δ +12.62 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0251, Δprecisión -0.1635, Δrecuperación +0.0217; N3: ΔF1 -0.0199, Δprecisión -0.0128, Δrecuperación -0.0368.

**Conclusión:** Mayor F1 promedio en 3/5 folds; la brecha no se redujo claramente. La ventaja media es pequeña, sin prueba de superioridad estadística. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 60. XGBoost · Contexto temporal · Historia 2 minutos

Prueba: `contexto_temporal_XGB_lag_2`. Referencia: `temporal_representacion_XGB_candidata`. Con pesos.

F1 macro **0.5567 → 0.5502 ± 0.0601** (Δ -0.0065). F1 entrenamiento 0.9527; brecha 0.4025 (Δ +0.0199). Entrenamiento total 31.44 s (Δ +12.13 s). Mayor F1 en 3/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0112, Δprecisión -0.1934, Δrecuperación +0.0116; N3: ΔF1 -0.0388, Δprecisión -0.0177, Δrecuperación -0.0801.

**Conclusión:** Menor F1 promedio; mejoró en 3/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 61. XGBoost · Contexto temporal · Historia 5 minutos

Prueba: `contexto_temporal_XGB_lag_5`. Referencia: `temporal_representacion_XGB_candidata`. Con pesos.

F1 macro **0.5567 → 0.5445 ± 0.0559** (Δ -0.0122). F1 entrenamiento 0.9524; brecha 0.4079 (Δ +0.0253). Entrenamiento total 32.41 s (Δ +13.10 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: W: ΔF1 +0.0039, Δprecisión +0.0017, Δrecuperación +0.0065; N3: ΔF1 -0.0432, Δprecisión -0.0329, Δrecuperación -0.0701.

**Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 62. XGBoost · Contexto temporal · Historia 10 minutos

Prueba: `contexto_temporal_XGB_lag_10`. Referencia: `temporal_representacion_XGB_candidata`. Con pesos.

F1 macro **0.5567 → 0.5341 ± 0.0544** (Δ -0.0226). F1 entrenamiento 0.9510; brecha 0.4169 (Δ +0.0342). Entrenamiento total 31.92 s (Δ +12.61 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: W: ΔF1 +0.0026, Δprecisión +0.0003, Δrecuperación +0.0054; N3: ΔF1 -0.0920, Δprecisión -0.0845, Δrecuperación -0.0992.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 63. XGBoost · Contexto temporal · Historia 15 minutos

Prueba: `contexto_temporal_XGB_lag_15`. Referencia: `temporal_representacion_XGB_candidata`. Con pesos.

F1 macro **0.5567 → 0.5467 ± 0.0631** (Δ -0.0100). F1 entrenamiento 0.9505; brecha 0.4038 (Δ +0.0212). Entrenamiento total 30.79 s (Δ +11.49 s). Mayor F1 en 2/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0056, Δprecisión -0.2058, Δrecuperación +0.0090; N3: ΔF1 -0.0316, Δprecisión -0.0205, Δrecuperación -0.0620.

**Conclusión:** Menor F1 promedio; mejoró en 2/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 64. XGBoost · Contexto temporal · Historia 5+10 minutos

Prueba: `contexto_temporal_XGB_lag_5+10`. Referencia: `temporal_representacion_XGB_candidata`. Con pesos.

F1 macro **0.5567 → 0.5409 ± 0.0581** (Δ -0.0158). F1 entrenamiento 0.9579; brecha 0.4170 (Δ +0.0343). Entrenamiento total 45.34 s (Δ +26.03 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0045, Δprecisión -0.2099, Δrecuperación +0.0093; N3: ΔF1 -0.0547, Δprecisión -0.0380, Δrecuperación -0.0879.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 65. XGBoost · Contexto temporal · Historia 1+2 minutos (dos mejores individuales)

Prueba: `contexto_temporal_XGB_lag_1+2`. Referencia: `temporal_representacion_XGB_candidata`. Con pesos.

F1 macro **0.5567 → 0.5803 ± 0.0698** (Δ +0.0236). F1 entrenamiento 0.9587; brecha 0.3784 (Δ -0.0043). Entrenamiento total 45.38 s (Δ +26.08 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0643, Δprecisión +0.0640, Δrecuperación +0.0520; N1: ΔF1 -0.0131, Δprecisión +0.0056, Δrecuperación -0.0387.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 66. XGBoost · Balanceo control · Misma configuración sin ponderación

Prueba: `balanceo_temporal_XGB_sin_pesos`. Referencia: `temporal_representacion_XGB_candidata`. Sin pesos.

F1 macro **0.5567 → 0.5139 ± 0.0617** (Δ -0.0428). F1 entrenamiento 0.9630; brecha 0.4491 (Δ +0.0664). Entrenamiento total 6.14 s (Δ -13.16 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: N2: ΔF1 +0.0080, Δprecisión -0.0639, Δrecuperación +0.0910; N3: ΔF1 -0.1106, Δprecisión +0.0683, Δrecuperación -0.2734.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 67. XGBoost · Balanceo control · Misma configuración con pesos balanceados

Prueba: `balanceo_temporal_XGB_pesos`. Referencia: `balanceo_temporal_XGB_sin_pesos`. Con pesos.

F1 macro **0.5139 → 0.5567 ± 0.0522** (Δ +0.0428). F1 entrenamiento 0.9394; brecha 0.3827 (Δ -0.0664). Entrenamiento total 6.99 s (Δ +0.84 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1106, Δprecisión -0.0683, Δrecuperación +0.2734; N2: ΔF1 -0.0080, Δprecisión +0.0639, Δrecuperación -0.0910.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

#### 68. XGBoost · Balanceo control · Escalado sin remuestreo ni pesos

Prueba: `balanceo_temporal_XGB_escala`. Referencia: `balanceo_temporal_XGB_sin_pesos`. Sin pesos.

F1 macro **0.5139 → 0.5101 ± 0.0603** (Δ -0.0037). F1 entrenamiento 0.9630; brecha 0.4529 (Δ +0.0038). Entrenamiento total 6.69 s (Δ +0.54 s). Mayor F1 en 1/5 folds.

Etapas con cambios extremos: REM: ΔF1 +0.0065, Δprecisión +0.0034, Δrecuperación +0.0052; N3: ΔF1 -0.0170, Δprecisión -0.0474, Δrecuperación -0.0043.

**Conclusión:** Menor F1 promedio; mejoró en 1/5 folds. **Decisión:** No priorizar para esta ronda según F1 macro.

#### 69. XGBoost · SMOTE · SMOTE objetivo 50% de mayoritaria; k=3

Prueba: `smote_temporal_XGB_ratio0.5_k3`. Referencia: `balanceo_temporal_XGB_escala`. Sin pesos.

F1 macro **0.5101 → 0.5322 ± 0.0522** (Δ +0.0221). F1 entrenamiento 0.9490; brecha 0.4168 (Δ -0.0360). Entrenamiento total 9.05 s (Δ +2.37 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.0474, Δprecisión -0.0460, Δrecuperación +0.1115; W: ΔF1 -0.0046, Δprecisión +0.0119, Δrecuperación -0.0232.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

Contra el ganador base `temporal_representacion_XGB_candidata` (F1 0.5567), ΔF1 -0.0245. No desplaza al ganador base por F1 medio, aunque mejore contra el control sin pesos.

#### 70. XGBoost · SMOTE · SMOTE objetivo 50% de mayoritaria; k=5

Prueba: `smote_temporal_XGB_ratio0.5_k5`. Referencia: `balanceo_temporal_XGB_escala`. Sin pesos.

F1 macro **0.5101 → 0.5503 ± 0.0548** (Δ +0.0401). F1 entrenamiento 0.9496; brecha 0.3994 (Δ -0.0535). Entrenamiento total 9.24 s (Δ +2.56 s). Mayor F1 en 5/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1107, Δprecisión +0.0152, Δrecuperación +0.1804; N2: ΔF1 +0.0011, Δprecisión +0.0331, Δrecuperación -0.0400.

**Conclusión:** Mayor F1 promedio en 5/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

Contra el ganador base `temporal_representacion_XGB_candidata` (F1 0.5567), ΔF1 -0.0064. No desplaza al ganador base por F1 medio, aunque mejore contra el control sin pesos.

#### 71. XGBoost · SMOTE · SMOTE objetivo 100% de mayoritaria; k=3

Prueba: `smote_temporal_XGB_ratio1.0_k3`. Referencia: `balanceo_temporal_XGB_escala`. Sin pesos.

F1 macro **0.5101 → 0.5540 ± 0.0550** (Δ +0.0438). F1 entrenamiento 0.9304; brecha 0.3764 (Δ -0.0764). Entrenamiento total 12.45 s (Δ +5.77 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1298, Δprecisión -0.0092, Δrecuperación +0.2580; N2: ΔF1 -0.0085, Δprecisión +0.0603, Δrecuperación -0.0889.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

Contra el ganador base `temporal_representacion_XGB_candidata` (F1 0.5567), ΔF1 -0.0027. No desplaza al ganador base por F1 medio, aunque mejore contra el control sin pesos.

#### 72. XGBoost · SMOTE · SMOTE objetivo 100% de mayoritaria; k=5

Prueba: `smote_temporal_XGB_ratio1.0_k5`. Referencia: `balanceo_temporal_XGB_escala`. Sin pesos.

F1 macro **0.5101 → 0.5639 ± 0.0588** (Δ +0.0537). F1 entrenamiento 0.9302; brecha 0.3663 (Δ -0.0866). Entrenamiento total 12.54 s (Δ +5.85 s). Mayor F1 en 4/5 folds.

Etapas con cambios extremos: N3: ΔF1 +0.1705, Δprecisión +0.0148, Δrecuperación +0.3291; N2: ΔF1 -0.0089, Δprecisión +0.0632, Δrecuperación -0.0926.

**Conclusión:** Mayor F1 promedio en 4/5 folds; también se redujo la brecha. **Decisión:** Conservar como candidato de esta ronda; no afirmar un óptimo global.

Contra el ganador base `temporal_representacion_XGB_candidata` (F1 0.5567), ΔF1 +0.0072. Conservar para la selección global, sin afirmar superioridad concluyente.

### Candidatos y límites

| Escenario | Candidato | F1 base | F1 candidato | Desviación | Exactitud | Brecha | Entrenamiento 5 folds (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Personas nuevas | contexto_pacientes_XGB_lag_1+2 | 0.4907 | 0.5053 | 0.0265 | 0.6043 | 0.3010 | 42.0055 |
| Pacientes conocidos: lecturas futuras | contexto_temporal_XGB_lag_1+2 | 0.5567 | 0.5803 | 0.0698 | 0.7050 | 0.3784 | 45.3840 |

- **Personas nuevas:** XGBoost, n_estimators=200, max_depth=4, learning_rate=0.1, min_child_weight=predeterminado, reg_lambda=5, subsample=0.8, colsample_bytree=0.8; con pesos; 68 predictores; historia 1+2 minutos; imputación por fold.
- **Pacientes conocidos: lecturas futuras:** XGBoost, n_estimators=200, max_depth=6, learning_rate=0.1, min_child_weight=predeterminado, reg_lambda=predeterminado, subsample=0.8, colsample_bytree=0.8; con pesos; 68 predictores; historia 1+2 minutos; imputación por fold.

La tabla conserva la selección de desarrollo. Para personas nuevas se congeló el candidato y luego se evaluó test, sin nuevos ajustes; ver cierre siguiente. El candidato cronológico sigue pendiente de una prueba independiente. Importancia: promedio de permutaciones en validación y desviación entre folds; no causalidad. Curvas/matrices acumuladas no equivalen a promedios de folds.

## Evaluación final del candidato congelado

Esta evaluación es posterior a los 147 contrastes de desarrollo; no es otra búsqueda de parámetros. Se conservaron sus resultados y se reentrenó únicamente XGBoost ponderado, profundidad 4, lambda 5, historia 1+2 minutos y 68 entradas, con todo desarrollo. La configuración quedó congelada antes de abrir test.

| Evaluación | F1 macro | Exactitud |
| --- | --- | --- |
| Validación por pacientes: media de cinco folds | 0.5053 | 0.6043 |
| Test: agregado de 16 personas nuevas | 0.5412 | 0.6126 |

El test obtuvo F1 macro **0.5412** y exactitud **0.6126** en 11.839 epochs de 16 pacientes. La diferencia frente a la media de validación es +0.0358. La cifra global mayor no prueba superioridad ni estabilidad universal: cambian las personas, la distribución y la cantidad de datos usada para entrenar. No se reajustaron parámetros, señales ni umbrales con este resultado.

**N1 sigue siendo la principal debilidad:** precisión 0.1733, recuperación 0.2958, F1 0.2185, AP 0.1699. Aproximadamente el 82.7 % de las detecciones N1 son falsas y se omite una proporción importante de sus casos reales. El resultado no justifica afirmar buen reconocimiento de todas las etapas.

**Conclusión y decisión:** conservar el modelo como resultado evaluado de esta ronda, con limitaciones por etapa y paciente. El mayor F1 global no demuestra superioridad estadística ni elimina la debilidad de N1. No realizar nuevas elecciones usando este test. La prueba temporal independiente, solo wearable y evaluación externa siguen pendientes; otras combinaciones requieren un nuevo ciclo con evaluación propia.

El detalle final y el guion para exposición están en el [informe](informe-modelado.md). Modelo y predicciones persistidos, lectura posterior protegida; ANTERIOR y las secciones previas permanecen intactos.
