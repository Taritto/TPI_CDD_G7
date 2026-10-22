# Informe de modelado · revisión, decisiones y exposición

## Problema y método

Clasificar epochs actuales de 30 segundos en cinco etapas del sueño utilizando wearable + PSG. Se consumen CSV preparados, sin repetir EDA/ETL. Se conserva una cohorte de desarrollo de 60 pacientes y una reserva histórica de 16; identidad, tiempo y etiquetas no entran como predictores. Los antecedentes incluyen señales anteriores, nunca etiquetas.

Se selecciona un candidato por pacientes separados y otro por epochs mezclados, con cinco folds y el mismo catálogo acotado. Separar pacientes estima generalización entre personas; mezclar permite compartir sujetos y observaciones próximas. Se necesita un conjunto común fuera de entrenamiento para contrastar los candidatos, no comparar directamente sus F1 de validación.

## Qué cambió respecto del estado recibido

La revisión recibida contenía salidas de Kaggle hasta 4.5.2, con 16 variantes individuales. Se completaron historia, balanceo, selección y diagnósticos sin ampliar hiperparámetros ni combinar historia con SMOTE. Se reemplazó la exigencia de CSV de pacientes adicionales por evaluación sobre los 16 pacientes ya reservados. El notebook oficial y el código/salidas de 4.8 permanecen como evidencia histórica.

El desarrollo nuevo se ejecutó desde un kernel limpio con `N_JOBS=-1`, CPU, semilla 42 y versiones registradas. No estaban disponibles las exportaciones completas de Kaggle de 4.1–4.5.2, por lo que se repitieron los bloques necesarios en vez de reconstruir predicciones desde tablas. Las salidas recibidas de Kaggle (`N_JOBS=2`) se conservaron como evidencia anterior; sus tiempos no son comparables directamente con esta ejecución. Los registros `ejecuciones.jsonl` distinguen entrenamiento ejecutado y reutilización compatible.

Antes de predecir el test, la comprobación binaria de serialización de RF detectó diferencias de redondeo de aproximadamente 3,3 × 10⁻¹⁶, sin cambiar clases. Se corrigió el control a tolerancia 10⁻¹² con clases idénticas y se agregó una prueba de regresión. Se conservó el estado interrumpido y se completó 4.7 en otro kernel limpio desde los dos pipelines guardados y verificados, sin reentrenarlos ni repetir predicciones de test. La continuación preapertura quedó auditada; el flujo normal sigue bloqueando estados incompletos. Los tiempos exactos de ese entrenamiento final no se habían persistido antes de la interrupción y se muestran ausentes, sin estimarlos. Sí están disponibles los costos de entrenamiento de validación y los tiempos reales de inferencia.

Las nuevas salidas viven en `output/modelado_revision/`. Los artefactos de comparación están en `comparacion_test/`: configuraciones congeladas, pipelines, pruebas de serialización, predicciones únicas, métricas, diagnósticos y diferencias por paciente. El notebook oficial y el código/salidas históricos de 4.8 se preservaron. No se ejecutó 4.8.

## Selección y resultados

| Selección | Algoritmo | Pesos | Historia (min) | Entradas | F1 validación ± DE | F1 test | Exactitud test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pacientes separados | XGB | Sí | [1, 2] | 68 | 0,5053 ± 0,0265 | 0,5412 | 0,6126 |
| Epochs mezclados | RF | No | Sin historia | 22 | 0,8006 ± 0,0038 | 0,4985 | 0,6278 |

- **Pacientes separados:** `contexto_pacientes_XGB_lag_1+2`; `n_estimators=200`, `max_depth=4`, `learning_rate=0.1`, `reg_lambda=5`, `min_child_weight=None`, `subsample=0.8`, `colsample_bytree=0.8`; representación `candidata`; pesos balanceados; retardos [1, 2]; SMOTE `None`; 68 entradas. Las opciones predeterminadas se registran en la configuración congelada.
- **Epochs mezclados:** `smote_epochs_RF_ratio1.0_k5`; `n_estimators=200`, `max_depth=None`, `min_samples_leaf=2`, `max_features=sqrt`; representación `candidata`; pesos desactivados; retardos []; SMOTE `{'ratio': 1.0, 'k': 5}`; 22 entradas. Las opciones predeterminadas se registran en la configuración congelada.

### Contexto y balanceo

| Protocolo | Prueba | Mejor variante observada | F1 referencia | F1 variante | Diferencia | Brecha | Entrenamiento 5 folds (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pacientes separados | Contexto temporal | Historia 1+2 minutos (dos mejores individuales) | 0,4907 | 0,5053 | 0,0147 | 0,3010 | 12,1839 |
| Pacientes separados | SMOTE | SMOTE objetivo 100% de mayoritaria; k=3 | 0,4451 | 0,4860 | 0,0409 | 0,2911 | 12,7084 |
| Epochs mezclados | Contexto temporal | Historia 15 minutos | 0,7860 | 0,7888 | 0,0029 | 0,1777 | 13,6455 |
| Epochs mezclados | SMOTE | SMOTE objetivo 100% de mayoritaria; k=5 | 0,7645 | 0,8006 | 0,0360 | 0,1947 | 38,1493 |

La referencia de SMOTE en la tabla es el control escalado sin pesos. Frente al control ponderado:

- **Pacientes separados:** mejor SMOTE 0,4860; control ponderado sin historia 0,4491; diferencia SMOTE menos ponderado 0,0369.
- **Epochs mezclados:** mejor SMOTE 0,8006; control ponderado sin historia 0,7617; diferencia SMOTE menos ponderado 0,0388.

La historia se construye dentro de paciente y segmento continuo; discontinuidades reinician antecedentes. Los faltantes se conservan como NaN e indicadores e imputan con medianas aprendidas en entrenamiento. SMOTE se aplica solo a entrenamiento, con control escalado; las métricas de entrenamiento se miden sobre filas reales. Más dimensiones, más ejemplos sintéticos o menor brecha no garantizan mayor F1.

La [guía](experimentos-hiperparametros.md) presenta para cada prueba la referencia, diferencias, tiempos, etapas y conclusión; no es una búsqueda exhaustiva ni una prueba de optimalidad.

## Comparación sobre el mismo test

En los mismos 16 pacientes, el candidato seleccionado mediante **pacientes separados** obtuvo el mayor F1 macro. Diferencia epochs menos pacientes: **-0,0426**. Las validaciones no se comparan como si midieran generalización equivalente. La diferencia en test corresponde a estos candidatos concretos; pueden cambiar algoritmo, entradas y parámetros además del protocolo. No se realizaron reajustes posteriores.

| Etapa | Pacientes separados: F1 test | Epochs mezclados: F1 test |
| --- | --- | --- |
| W | 0,6077 | 0,6188 |
| N1 | 0,2185 | 0,2048 |
| N2 | 0,7637 | 0,7819 |
| N3 | 0,5832 | 0,3734 |
| REM | 0,5327 | 0,5138 |

- **Pacientes separados:** menor F1 en N1: 0,2185, precisión 0,1733, recuperación 0,2958. F1 individual entre 0,1913 y 0,6369; 11/16 personas sin las cinco etapas observadas. No afirmar buen reconocimiento uniforme.
- **Epochs mezclados:** menor F1 en N1: 0,2048, precisión 0,1789, recuperación 0,2394. F1 individual entre 0,2137 y 0,5493; 11/16 personas sin las cinco etapas observadas. No afirmar buen reconocimiento uniforme.

El candidato de epochs mezclados supera al de pacientes en 6 de los 16 F1 individuales, calculados sobre cinco clases fijas. Etapas ausentes y distintas duraciones limitan la comparación. El agregado por epoch da más peso a registros largos. Revisar las tablas por paciente y matrices en 4.7, no solo el promedio global.

Los gráficos ROC complementan precisión/recuperación; una ROC-AUC alta puede coexistir con mala precisión de una etapa escasa. La importancia de los mejores RF/XGBoost base se conserva y se añadió un análisis específico del XGBoost final de 68 entradas. Ambos miden caída de F1 en validación; no demuestran causalidad.

## Interpretación del XGBoost final con historia

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

## Lectura de la decisión final

XGBoost obtuvo F1 macro de test 0,5412 frente a 0,4985 de RF, aunque RF tuvo mayor exactitud (0,6278 frente a 0,6126). La validación por pacientes ya exigía predecir personas excluidas del entrenamiento; mezclar epochs permitía compartir personas y observaciones próximas. Esa diferencia ayuda a entender por qué la validación mezclada fue más favorable, pero no demuestra que el protocolo sea la única causa del resultado: también cambiaron algoritmo, regularización, ponderación, historia y SMOTE. La importancia describe al XGBoost, no prueba por qué superó a RF.

N1 sigue siendo débil: F1 0,2185, precisión 0,1733 y recuperación 0,2958. El F1 por persona varía entre 0,1913 y 0,6369; la cobertura de etapas limita comparaciones individuales. El test tuvo exposición histórica y no constituye una nueva evaluación independiente.


## Límites y decisiones

El test ya había sido consultado y tuvo exposición histórica en EDA/comparaciones de la cohorte completa. Esta es una comparación posterior sobre personas excluidas de los nuevos entrenamientos, **no una nueva prueba independiente**. No se usó para seleccionar ni reajustar los candidatos de esta ronda. La selección entre muchas pruebas puede optimizar en exceso la validación.

Al mezclar epochs se comparten personas y observaciones próximas. Con historia, un antecedente puede contener señales de otro fold; no contiene su etiqueta, pero la dependencia puede favorecer las métricas. Las etapas ausentes y las distintas duraciones limitan comparaciones individuales. Los modelos utilizan wearable + PSG; no demuestran rendimiento solo wearable.

Se conservan ambos candidatos y sus resultados; no se reemplaza ni se reajusta automáticamente el pipeline histórico. El F1 histórico 0,5412 de 4.8 pertenece a otra selección y ejecución, aunque use los mismos 16 pacientes. Una evaluación externa con personas adicionales sería una ampliación futura y requeriría entradas compatibles; no es necesaria para consultar los resultados actuales.

## Síntesis para exposición

1. **Problema:** reconocer cinco etapas del sueño en epochs de 30 segundos con wearable + PSG.
2. **Metodología:** dos estrategias de selección, mismas fuentes de desarrollo y mismo catálogo, con pesos, representación, historia y SMOTE controlados.
3. **Evidencia:** comparar ambos candidatos congelados sobre los mismos 16 pacientes fuera de entrenamiento; mostrar F1 macro y errores por etapa/persona.
4. **Interpretación:** las señales actuales y los antecedentes se analizan mediante importancia individual y conjunta en validación; no se usan para reajustar el modelo.
5. **Decisión observada:** En los mismos 16 pacientes, el candidato seleccionado mediante **pacientes separados** obtuvo el mayor F1 macro. Diferencia epochs menos pacientes: **-0,0426**. Las validaciones no se comparan como si midieran generalización equivalente. La diferencia en test corresponde a estos candidatos concretos; pueden cambiar algoritmo, entradas y parámetros además del protocolo. No se realizaron reajustes posteriores.
6. **Límites:** test históricamente consultado, validación mezclada dependiente y heterogeneidad por paciente. No afirmar que un protocolo sea universalmente superior.
7. **Continuidad:** ronda actual terminada; nuevos experimentos necesitarían otra justificación y evaluación, sin reajustar a partir de este test.

## Evidencia histórica · informe previo

El contenido siguiente conserva el recorrido y los resultados anteriores; los pendientes y protocolos antiguos no describen el alcance activo.



El contenido siguiente conserva el recorrido y los resultados anteriores; los pendientes y protocolos antiguos no describen el alcance activo.

## Objetivo y alcance

Predecir la etapa del sueño de un epoch de 30 segundos: W, N1, N2, N3 o REM. El notebook recibe dos CSV ya preparados; no reconstruye señales ni repite EDA/ETL. El escenario actual dispone de wearable y PSG: no demuestra desempeño de un dispositivo wearable aislado.

La cátedra solicita seleccionar técnicas, ajustar parámetros, evaluar e interpretar. Los protocolos por paciente, validación cronológica, XGBoost, historia y SMOTE son decisiones metodológicas del proyecto, no algoritmos exigidos por la consigna.

## Desde la versión anterior hasta el flujo actual

La versión anterior comparaba modelos sobre los 76 pacientes sin test interno reservado. Sus métricas y configuraciones se conservaron en [referencia-previa.json](referencia-previa.json); el notebook ANTERIOR permaneció intacto. XGBoost ponderado alcanzaba F1 macro 0,4923; RF sin pesos tenía mayor exactitud (0,6612). Son antecedentes de otra partición: no sirven para atribuir mejoras causales frente a desarrollo reducido.

Se independizó modelado del ETL, validó la coincidencia completa de CSV y reservó 20 % de pacientes con semilla 42. Se guardaron asignaciones y huellas; identificadores y objetivo se excluyen de predictores. Se recuperaron explicaciones de modelos, parámetros, pesos y métricas y se reemplazaron tablas extensas por resúmenes legibles.

Se compararon referencias Dummy/logística/RF/XGBoost, ponderación, variantes individuales de hiperparámetros y representaciones. Luego se ampliaron las pruebas a dos escenarios de uso, contexto temporal y SMOTE. Los diagnósticos se separaron en importancia, errores, PR, ROC y pacientes. Cada prueba tiene referencia y conclusión en la [guía](experimentos-hiperparametros.md).

Dos escenarios de selección, sin consultar el test. Desarrollo: 45.011 epochs de 60 pacientes; reserva: 11.839 epochs de 16 pacientes. El protocolo por pacientes evalúa todos los epochs de desarrollo. El cronológico evalúa 37.490 epochs; excluye de validación los 7.521 del bloque inicial, conservados para entrenamiento. Cinco folds por escenario; gap cronológico de 15 minutos.

Se ejecutaron 147 comparaciones documentadas: Hiperparámetro: 84, Protocolo: 14, Contexto temporal: 14, Pesos: 9, SMOTE: 8, Representación: 8, Balanceo control: 6, Control: 4. Las referencias de epochs mezclados se conservan como diagnóstico. Las cifras son de desarrollo, no de prueba final.

## Qué pregunta responde cada protocolo

| Modelo | Pesos | Pacientes separados | Epochs mezclados | Cronológico |
| --- | --- | --- | --- | --- |
| RF | No | 0.3847 ± 0.0284 | 0.7617 ± 0.0083 | 0.4822 ± 0.0591 |
| RF | Sí | 0.4412 ± 0.0288 | 0.7860 ± 0.0081 | 0.5424 ± 0.0681 |
| XGB | No | 0.4465 ± 0.0322 | 0.7418 ± 0.0077 | 0.5133 ± 0.0604 |
| XGB | Sí | 0.4859 ± 0.0299 | 0.7273 ± 0.0052 | 0.5452 ± 0.0448 |

**Personas nuevas:** pacientes completos separados entre entrenamiento y validación. Es la evidencia pertinente para una persona no vista al entrenar.

**Pacientes conocidos:** entrenamiento creciente con observaciones anteriores de cada paciente y cinco bloques futuros de validación. Se deja un gap de 15 minutos. Este escenario presupone datos pasados etiquetados disponibles para entrenar; tener únicamente señales pasadas sin anotaciones no equivale a haber entrenado con esa persona. Las etiquetas pasadas se usan como objetivo de entrenamiento, nunca como características de entrada al predecir. El inicio de la noche ofrece pocos ejemplos de ciertas etapas; el cambio de distribución a lo largo de la noche forma parte de este escenario.

**Epochs mezclados:** personas y momentos próximos aparecen en ambos conjuntos. Su F1 mayor puede reflejar semejanza entre registros conocidos; no demuestra generalización a personas nuevas ni al futuro. Ambos candidatos predicen epochs: el protocolo es una regla de evaluación, no otra unidad de salida.

## Algoritmos, pesos y ajustes

Dummy establece un piso sin distinguir etapas. Logística ofrece una referencia lineal; RF y XGBoost representan interacciones no lineales. Todos se comparan con los mismos folds dentro de cada escenario.

Los pesos cambian el costo de errores por clase y se calculan solo con entrenamiento. Pueden elevar recuperación minoritaria y también falsas alarmas; no garantizan mayor exactitud ni F1. Se variaron C, profundidad, tamaño de hojas, cantidad de árboles/rondas, muestreo, tasa y regularización, según el algoritmo. Variar un parámetro no demuestra que una combinación posterior será mejor.

### Personas nuevas · ajustes y representación

- **Logistica:** `ajuste_Logistica_pesos1_C_10`; F1 0.3469 ± 0.0388, brecha 0.0729.
- **RF:** `representacion_RF_separada_con_log`; F1 0.4680 ± 0.0302, brecha 0.3731.
- **XGB:** `representacion_XGB_candidata`; F1 0.4907 ± 0.0327, brecha 0.2879.

| Representación | Modelo | ΔF1 | Lectura |
| --- | --- | --- | --- |
| Sin log1p; canales combinados | Random Forest | -0.0001 | Sin prioridad frente a la referencia por F1 macro. |
| Canales separados; conservar log1p | Random Forest | 0.0066 | Conservar como candidato de esta ronda; no afirmar un óptimo global. |
| Sin log1p; canales combinados | XGBoost | 0.0000 | Sin prioridad frente a la referencia por F1 macro. |
| Canales separados; conservar log1p | XGBoost | -0.0093 | No priorizar para esta ronda según F1 macro. |

### Pacientes conocidos: lecturas futuras · ajustes y representación

- **Logistica:** `temporal_ajuste_Logistica_pesos1_C_10`; F1 0.3685 ± 0.0345, brecha 0.0983.
- **RF:** `temporal_representacion_RF_separada_con_log`; F1 0.5526 ± 0.0730, brecha 0.4052.
- **XGB:** `temporal_representacion_XGB_candidata`; F1 0.5567 ± 0.0522, brecha 0.3827.

| Representación | Modelo | ΔF1 | Lectura |
| --- | --- | --- | --- |
| Sin log1p; canales combinados | Random Forest | 0.0002 | Sin prioridad frente a la referencia por F1 macro. |
| Canales separados; conservar log1p | Random Forest | 0.0066 | Conservar como candidato de esta ronda; no afirmar un óptimo global. |
| Sin log1p; canales combinados | XGBoost | 0.0000 | Sin prioridad frente a la referencia por F1 macro. |
| Canales separados; conservar log1p | XGBoost | -0.0110 | No priorizar para esta ronda según F1 macro. |

**Lección de regularización:** aumentar las hojas de RF no tiene el mismo efecto en ambos escenarios. Una menor brecha no alcanza para recomendar el cambio:

| Escenario | RF pesos: hoja 2 → 10 | Δ F1 | Δ brecha |
| --- | --- | --- | --- |
| Personas nuevas | 0.4412 → 0.4614 | 0.0201 | -0.1430 |
| Pacientes conocidos: lecturas futuras | 0.5424 → 0.5188 | -0.0236 | -0.0953 |

En XGBoost ponderado para pacientes conocidos, profundidad 4 → 6 elevó F1 0.5452 → 0.5567, pero la brecha creció de 0.2952 a 0.3827. Hay mayor capacidad y mejor validación observada, junto con más separación respecto del entrenamiento; no corresponde declarar eliminado el sobreajuste.

Distribución del primer fold cronológico; permite interpretar la escasez inicial de algunas etapas:

| etapa | entrenamiento | validacion |
| --- | --- | --- |
| W | 1220 | 1488 |
| N1 | 884 | 789 |
| N2 | 3117 | 4138 |
| N3 | 471 | 533 |
| R | 29 | 569 |

## Contexto temporal: qué se probó y qué ocurrió

Se agregó el pasado de las mismas señales utilizadas por el ganador base de cada escenario, manteniendo modelo e hiperparámetros. Se probaron 1, 2, 5, 10 y 15 minutos, 5+10 y los dos retardos individuales mejor posicionados. La búsqueda es acotada: no identifica el mejor tiempo posible fuera de esa grilla.

Cada paciente y discontinuidad reinicia historia. Si no existe antecedente, se conserva NaN y un indicador de disponibilidad; la mediana se ajusta dentro del entrenamiento. No se usan etapas reales anteriores, datos futuros ni historia de otro paciente. Al predecir secuencialmente sí pueden utilizarse señales de epochs de validación anteriores: estarían disponibles en uso real sin conocer su etiqueta.

### Personas nuevas

| Historia | F1 macro | ΔF1 | Brecha | Entrenamiento (s) |
| --- | --- | --- | --- | --- |
| Historia 1 minutos | 0.4964 | 0.0058 | 0.3023 | 29.7137 |
| Historia 2 minutos | 0.4940 | 0.0033 | 0.3025 | 28.2759 |
| Historia 5 minutos | 0.4881 | -0.0026 | 0.3053 | 28.6059 |
| Historia 10 minutos | 0.4916 | 0.0009 | 0.3008 | 28.0415 |
| Historia 15 minutos | 0.4927 | 0.0021 | 0.2993 | 28.2097 |
| Historia 5+10 minutos | 0.4893 | -0.0014 | 0.3110 | 40.2214 |
| Historia 1+2 minutos (dos mejores individuales) | 0.5053 | 0.0147 | 0.3010 | 42.0055 |

**Resultado:** Historia 1+2 minutos (dos mejores individuales) obtuvo la mayor media temporal (0.5053; Δ +0.0147). Mayor F1 promedio en 4/5 folds; la brecha no se redujo claramente. Conservar como candidato de esta ronda; no afirmar un óptimo global.

Disponibilidad de ese contexto en desarrollo completo:

| minutos | disponibles | faltantes | fraccion |
| --- | --- | --- | --- |
| 1 | 44889 | 122 | 0.9973 |
| 2 | 44767 | 244 | 0.9946 |

### Pacientes conocidos: lecturas futuras

| Historia | F1 macro | ΔF1 | Brecha | Entrenamiento (s) |
| --- | --- | --- | --- | --- |
| Historia 1 minutos | 0.5601 | 0.0034 | 0.3934 | 31.9296 |
| Historia 2 minutos | 0.5502 | -0.0065 | 0.4025 | 31.4355 |
| Historia 5 minutos | 0.5445 | -0.0122 | 0.4079 | 32.4101 |
| Historia 10 minutos | 0.5341 | -0.0226 | 0.4169 | 31.9166 |
| Historia 15 minutos | 0.5467 | -0.0100 | 0.4038 | 30.7936 |
| Historia 5+10 minutos | 0.5409 | -0.0158 | 0.4170 | 45.3355 |
| Historia 1+2 minutos (dos mejores individuales) | 0.5803 | 0.0236 | 0.3784 | 45.3840 |

**Resultado:** Historia 1+2 minutos (dos mejores individuales) obtuvo la mayor media temporal (0.5803; Δ +0.0236). Mayor F1 promedio en 4/5 folds; también se redujo la brecha. Conservar como candidato de esta ronda; no afirmar un óptimo global.

Disponibilidad de ese contexto en desarrollo completo:

| minutos | disponibles | faltantes | fraccion |
| --- | --- | --- | --- |
| 1 | 44889 | 122 | 0.9973 |
| 2 | 44767 | 244 | 0.9946 |

Los indicadores también pueden reflejar tiempo transcurrido y comienzo de segmentos. El experimento no separa ese aporte del contenido fisiológico de las señales pasadas. No atribuir la diferencia únicamente a transiciones del sueño. Incorporar historia aumenta dimensiones y puede elevar el costo. Los tiempos de entrenamiento incluyen el preprocesamiento ajustado dentro del pipeline y excluyen la construcción previa de historia, importancia y gráficos. Son mediciones de esta corrida, sensibles a la carga y al calentamiento del equipo: una diferencia de tiempo no demuestra por sí sola un efecto del parámetro.

## SMOTE: balancear no garantiza mejorar

Se compararon la misma configuración sin pesos, con pesos, escalada sin remuestreo y cuatro variantes SMOTE. Los vecinos 3/5 y objetivos por clase de 50/100 % se calcularon dentro de entrenamiento; validación y test mantienen frecuencias reales. SMOTE interpola entre ejemplos de una clase: no aporta pacientes nuevos y puede producir combinaciones fisiológicamente poco representativas. No se combinó con pesos ni historia temporal.

### Personas nuevas

| Cambio | F1 macro | Δ contra referencia | Brecha | Entrenamiento (s) |
| --- | --- | --- | --- | --- |
| Misma configuración sin ponderación | 0.4491 | -0.0416 | 0.3507 | 17.8360 |
| Misma configuración con pesos balanceados | 0.4907 | 0.0416 | 0.2879 | 17.7556 |
| Escalado sin remuestreo ni pesos | 0.4451 | -0.0040 | 0.3545 | 17.7107 |
| SMOTE objetivo 50% de mayoritaria; k=3 | 0.4830 | 0.0379 | 0.3147 | 27.1920 |
| SMOTE objetivo 50% de mayoritaria; k=5 | 0.4818 | 0.0367 | 0.3148 | 27.2908 |
| SMOTE objetivo 100% de mayoritaria; k=3 | 0.4860 | 0.0409 | 0.2911 | 42.1537 |
| SMOTE objetivo 100% de mayoritaria; k=5 | 0.4806 | 0.0355 | 0.2926 | 12.5915 |

**Resultado:** mejor SMOTE 0.4860; frente al ganador base 0.4907, diferencia -0.0046. No reemplazar al ganador base por SMOTE según estas medias.

Efecto frente al ganador base sobre las etapas minoritarias:

| Etapa | Δ precisión | Δ recuperación | Δ F1 |
| --- | --- | --- | --- |
| N1 | -0.0043 | -0.0088 | -0.0065 |
| N3 | 0.0110 | -0.0288 | -0.0038 |

### Pacientes conocidos: lecturas futuras

| Cambio | F1 macro | Δ contra referencia | Brecha | Entrenamiento (s) |
| --- | --- | --- | --- | --- |
| Misma configuración sin ponderación | 0.5139 | -0.0428 | 0.4491 | 6.1448 |
| Misma configuración con pesos balanceados | 0.5567 | 0.0428 | 0.3827 | 6.9855 |
| Escalado sin remuestreo ni pesos | 0.5101 | -0.0037 | 0.4529 | 6.6856 |
| SMOTE objetivo 50% de mayoritaria; k=3 | 0.5322 | 0.0221 | 0.4168 | 9.0537 |
| SMOTE objetivo 50% de mayoritaria; k=5 | 0.5503 | 0.0401 | 0.3994 | 9.2449 |
| SMOTE objetivo 100% de mayoritaria; k=3 | 0.5540 | 0.0438 | 0.3764 | 12.4528 |
| SMOTE objetivo 100% de mayoritaria; k=5 | 0.5639 | 0.0537 | 0.3663 | 12.5369 |

**Resultado:** mejor SMOTE 0.5639; frente al ganador base 0.5567, diferencia +0.0072. Conservar como alternativa por la mayor media observada, revisando etapas y costo.

Efecto frente al ganador base sobre las etapas minoritarias:

| Etapa | Δ precisión | Δ recuperación | Δ F1 |
| --- | --- | --- | --- |
| N1 | -0.0001 | -0.0005 | 0.0000 |
| N3 | 0.0357 | 0.0513 | 0.0429 |

## Selección de desarrollo y decisión

| Escenario | Candidato | F1 base | F1 candidato | Desviación | Exactitud | Brecha | Entrenamiento 5 folds (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Personas nuevas | contexto_pacientes_XGB_lag_1+2 | 0.4907 | 0.5053 | 0.0265 | 0.6043 | 0.3010 | 42.0055 |
| Pacientes conocidos: lecturas futuras | contexto_temporal_XGB_lag_1+2 | 0.5567 | 0.5803 | 0.0698 | 0.7050 | 0.3784 | 45.3840 |

### Personas nuevas

**Configuración:** XGBoost, n_estimators=200, max_depth=4, learning_rate=0.1, min_child_weight=predeterminado, reg_lambda=5, subsample=0.8, colsample_bytree=0.8; con pesos; 68 predictores; historia 1+2 minutos; imputación por fold.

**Debilidad:** N1 tiene F1 medio 0.2411, precisión 0.2375 y recuperación 0.2622. Brecha global 0.3010.

| Etapa | Precisión | Recuperación | F1 medio entre folds |
| --- | --- | --- | --- |
| W | 0.5818 | 0.5978 | 0.5757 |
| N1 | 0.2375 | 0.2622 | 0.2411 |
| N2 | 0.8431 | 0.7026 | 0.7657 |
| N3 | 0.4588 | 0.5977 | 0.4999 |
| R | 0.4208 | 0.5089 | 0.4442 |

En OOF acumulado, N1: F1 0.2417, AP 0.2173, ROC-AUC 0.7030. Estos agregados no equivalen al promedio entre folds.

**Uso:** necesita el epoch actual y señales pasadas opcionales, procesadas con las mismas reglas de continuidad y faltantes.

### Pacientes conocidos: lecturas futuras

**Configuración:** XGBoost, n_estimators=200, max_depth=6, learning_rate=0.1, min_child_weight=predeterminado, reg_lambda=predeterminado, subsample=0.8, colsample_bytree=0.8; con pesos; 68 predictores; historia 1+2 minutos; imputación por fold.

**Debilidad:** N1 tiene F1 medio 0.3351, precisión 0.3071 y recuperación 0.3792. Brecha global 0.3784.

| Etapa | Precisión | Recuperación | F1 medio entre folds |
| --- | --- | --- | --- |
| W | 0.7070 | 0.7690 | 0.7363 |
| N1 | 0.3071 | 0.3792 | 0.3351 |
| N2 | 0.8243 | 0.8330 | 0.8274 |
| N3 | 0.5277 | 0.7044 | 0.5986 |
| R | 0.5552 | 0.3277 | 0.4042 |

En OOF acumulado, N1: F1 0.3452, AP 0.2952, ROC-AUC 0.7804. Estos agregados no equivalen al promedio entre folds.

**Uso:** necesita el epoch actual y señales pasadas opcionales, procesadas con las mismas reglas de continuidad y faltantes.

## Importancia, errores y lectura de métricas

La importancia por permutación se calcula en validación de los mejores RF/XGBoost sin historia/SMOTE, con cinco repeticiones por fold. Es caída de F1 al desordenar una señal, no porcentaje explicado ni causalidad. Se presenta por separado de los diagnósticos de candidatos finales. Correlaciones pueden esconder aportes compartidos.

- **Personas nuevas · RF:** C4-M1_std (0.0301 ± 0.0215), F4-M1_std (0.0258 ± 0.0107), Fp1-O2_std (0.0255 ± 0.0180).
- **Personas nuevas · XGB:** EOG_max_std (0.0580 ± 0.0116), CZ - T4_std (0.0463 ± 0.0317), F4-M1_std (0.0446 ± 0.0218).
- **Pacientes conocidos: lecturas futuras · RF:** C4-M1_std (0.0708 ± 0.0343), Fp1-O2_std (0.0581 ± 0.0503), F4-M1_std (0.0562 ± 0.0431).
- **Pacientes conocidos: lecturas futuras · XGB:** C4-M1_std (0.0642 ± 0.0203), EOG_max_std (0.0633 ± 0.0338), F4-M1_std (0.0551 ± 0.0404).

F1 macro da igual peso a las cinco etapas; exactitud refleja todos los aciertos y puede favorecer N2. Precisión evalúa falsas detecciones; recuperación, casos omitidos; soporte, cantidad real. Mirar siempre las cinco etapas. Una brecha menor no basta si cae validación.

PR muestra precisión frente a recuperación y AP resume su curva; prevalencia es la referencia. ROC-AUC mide separación frente al resto, pero un AUC alto no garantiza precisión útil para una etapa rara. Matrices identifican confusiones concretas; el análisis por paciente muestra heterogeneidad oculta por promedios. Las figuras completas están en 4.6 del notebook.

## Evaluación final · configuración congelada

Se reentrenó únicamente el ganador para personas nuevas con todo desarrollo (45.011 epochs/60 pacientes). Se aprendieron allí los pesos y medianas; no se utilizó test para entrenar, detener, seleccionar ni ajustar umbrales. La configuración, fuentes, partición y versiones se guardaron antes de obtener métricas del test. El pipeline se guardó y cargó, comprobando igualdad de probabilidades en una muestra de desarrollo; luego realizó una única inferencia sobre test.

| Evaluación | F1 macro | Exactitud |
| --- | --- | --- |
| Validación por pacientes: media de cinco folds | 0.5053 | 0.6043 |
| Test: agregado de 16 personas nuevas | 0.5412 | 0.6126 |

El test obtuvo F1 macro **0.5412** y exactitud **0.6126** en 11.839 epochs de 16 pacientes. La diferencia frente a la media de validación es +0.0358. La cifra global mayor no prueba superioridad ni estabilidad universal: cambian las personas, la distribución y la cantidad de datos usada para entrenar. No se reajustaron parámetros, señales ni umbrales con este resultado.

| Etapa | Precisión | Recuperación | F1 | Soporte |
| --- | --- | --- | --- | --- |
| W | 0.6597 | 0.5633 | 0.6077 | 2842 |
| N1 | 0.1733 | 0.2958 | 0.2185 | 1224 |
| N2 | 0.8708 | 0.6801 | 0.7637 | 6076 |
| N3 | 0.6023 | 0.5653 | 0.5832 | 375 |
| R | 0.4245 | 0.7148 | 0.5327 | 1322 |

**N1 sigue siendo la principal debilidad:** precisión 0.1733, recuperación 0.2958, F1 0.2185, AP 0.1699. Aproximadamente el 82.7 % de las detecciones N1 son falsas y se omite una proporción importante de sus casos reales. El resultado no justifica afirmar buen reconocimiento de todas las etapas.

F1 por paciente, usando cinco clases fijas: mínimo 0.1913, máximo 0.6369. 11 de los 16 pacientes no tienen las cinco etapas observadas; esa cobertura limita comparaciones individuales. La heterogeneidad y los errores de N1 siguen siendo límites relevantes.

En N3, ROC-AUC 0.9746, AP 0.6036 y precisión 0.6023: AUC alto no implica detecciones casi siempre correctas. Las matrices, PR, ROC y los 16 pacientes se muestran en apartados separados de 4.8.

**Decisión:** conservar el modelo evaluado como resultado de esta ronda. El F1 global supera la media de validación, pero no corresponde afirmar rendimiento uniforme ni buen reconocimiento de N1. No se modificaron parámetros, predictores ni umbrales después del test. La evaluación externa sigue siendo necesaria para estudiar generalización fuera de esta cohorte.

**Uso posterior:** cargar `output/modelado/test_final/pipeline.joblib` y construir las mismas 68 columnas, con señales actuales e historia opcional de 1+2 minutos. Antecedentes ausentes se indican y completan con las medianas ya aprendidas; no se recalculan con datos nuevos. El archivo UBJ contiene solo XGBoost, no la imputación.

**Verificación:** 19 pruebas de integración; 4.8 completo probado en kernel limpio sintético; evaluación real en otro kernel limpio; relectura en una sesión nueva con entrenamiento/inferencia bloqueados. Coinciden las huellas de las secciones anteriores, exportaciones y ANTERIOR. Predicciones únicas y resultados protegidos mediante hashes; una ejecución posterior lee los archivos sin reabrir el test.

## Límites y próximos pasos

- Las configuraciones se seleccionaron usando validación repetidamente; el mayor F1 observado puede ser optimista. Diferencias pequeñas no prueban superioridad estadística y desviación entre folds no es intervalo de confianza.
- La configuración para personas nuevas se congeló y el test fue evaluado una vez. Tuvo exposición histórica en EDA/comparaciones anteriores: no presentarlo como históricamente intacto.
- El test por pacientes nuevos evalúa ese escenario. Para pacientes conocidos falta una evaluación temporal independiente de la selección. No promediar validación y test ni ajustar después de consultar la prueba final.
- Los datos son wearable + PSG; solo wearable sigue pendiente. También quedan combinaciones de hiperparámetros, SMOTE+historia y evaluación externa con pacientes adicionales.
- Decisión actual: conservar la configuración evaluada, con sus debilidades explícitas. Siguiente evaluación: pacientes externos; futuras mejoras requieren otra evaluación independiente, sin optimizar sobre este test.

## Guion breve para exponer

1. **Problema:** clasificar cada epoch en cinco etapas con señales fisiológicas; desbalance y diferencias entre personas dificultan la tarea.
2. **Método:** preservar antecedentes, reservar pacientes para test y comparar referencias, pesos, parámetros y representaciones dentro de desarrollo.
3. **Hallazgo metodológico:** mezclar epochs produce cifras diferentes de evaluar personas nuevas o futuro cronológico; responden preguntas distintas.
4. **Experimentos:** señales pasadas y SMOTE se midieron por separado sobre los mejores modelos base, manteniendo referencias explícitas y sin etiquetas previas.
5. **Decisión:** congelar XGBoost ponderado con historia 1+2 para personas nuevas; en test F1 0,5412 y exactitud 0,6126. N1 sigue débil y el rendimiento varía entre personas; el escenario conocido conserva su validación, sin prueba independiente.
6. **Cierre:** el test ya se evaluó sin reajustes. Conservar evidencia y contrastar pacientes externos y disponibilidad real de señales.

Referencias: [README de entrega](README.md), [guía de cada prueba](experimentos-hiperparametros.md), [ADR de evaluación](../adr/0011-modelado-posterior-a-la-entrega-etl.md), [ADR de balanceo](../adr/0009-distribuciones-y-desbalance-de-etapas.md).
