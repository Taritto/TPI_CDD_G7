# Resumen del notebook de revisión · Entrega 3

La [revisión](../../temporal_version_tp_entrega03_revision.ipynb) completa el modelado para clasificar cada epoch de 30 segundos en W, N1, N2, N3 o REM con wearable + PSG. La [guía](experimentos-hiperparametros.md) detalla cada prueba y el [informe](informe-modelado.md) integra la evidencia para exponer.

## 4.1 · Datos y particiones

Carga los dos CSV existentes sin repetir EDA/ETL, comprueba alineación, claves, entradas finitas y cinco etapas. Conserva los 60 pacientes de desarrollo (45.011 epochs) y los 16 de test histórico (11.839 epochs), sin pacientes compartidos. Usa cinco folds por pacientes y cinco estratificados por epochs mezclados, semilla 42; cada epoch recibe una predicción de validación por configuración.

## 4.2 · Referencias y parámetros

Dummy predice la etapa mayoritaria; logística ofrece una referencia lineal con escalado; RF y XGBoost capturan interacciones no lineales. Define configuraciones iniciales, pesos y recursos de CPU. Los valores iniciales no se consideran óptimos.

## 4.3 · Evaluación común

Un fold es una partición retenida para validar mientras las restantes entrenan; se rota cinco veces. El pipeline se ajusta desde cero por fold. Pesos: `N_train / (5 × N_clase_train)`, calculados solo en entrenamiento. No duplican observaciones. Escalado, imputación y SMOTE tampoco ven validación.

F1 combina precisión y recuperación; F1 macro promedia las cinco etapas por igual. Exactitud cuenta aciertos totales y soporte cuenta casos reales. Se guardan métricas por etapa/fold, brecha entrenamiento–validación, tiempos y probabilidades OOF. Menor brecha no significa mejor predicción si baja la validación.

## 4.4 · Comparación de protocolos

Compara las mismas referencias con/sin pesos bajo pacientes separados y epochs mezclados. Compartir personas y epochs próximos favorece la validación mezclada, pero no demuestra mejor generalización. Se conservan dos candidatos para evaluarlos después sobre las mismas personas reservadas.

## 4.5 · Selección y experimentos

- **4.5.1:** 16 variantes individuales de RF/XGBoost, catálogo reducido y sin combinaciones simultáneas. Selecciona por F1 macro medio; desempata con dispersión, tiempo y nombre. Logística no ajusta C.
- **Pruebas históricas de 4.5.1:** seis ejemplos recuperados de parámetros con pacientes separados y 22 entradas sin historia. Se verificaron fuentes/versiones/folds; no se agregaron a la selección congelada.
- **4.5.2:** contrasta canales combinados/separados manteniendo `log1p`, con hiperparámetros fijos por algoritmo. Elige el ganador base de cada protocolo.
- **4.5.3:** prueba señales pasadas de 1/2/5/10/15 minutos y combinaciones. Respeta paciente y continuidad; sin antecedentes conserva NaN e indicador e imputa con entrenamiento. No usa etiquetas anteriores ni señales futuras.
- **4.5.4:** compara pesos, escalado y SMOTE vecinos 3/5 con objetivos 50/100 % por clase. Solo entrena con ejemplos sintéticos; las métricas se calculan sobre observaciones reales. No combina SMOTE con historia.
- **4.5.5:** integra todas las pruebas y congela un candidato por protocolo, sus columnas, parámetros, representación, retardos y balanceo.

| Protocolo | Prueba | Mejor variante observada | F1 referencia | F1 variante | Diferencia | Brecha | Entrenamiento 5 folds (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pacientes separados | Contexto temporal | Historia 1+2 minutos (dos mejores individuales) | 0,4907 | 0,5053 | 0,0147 | 0,3010 | 12,1839 |
| Pacientes separados | SMOTE | SMOTE objetivo 100% de mayoritaria; k=3 | 0,4451 | 0,4860 | 0,0409 | 0,2911 | 12,7084 |
| Epochs mezclados | Contexto temporal | Historia 15 minutos | 0,7860 | 0,7888 | 0,0029 | 0,1777 | 13,6455 |
| Epochs mezclados | SMOTE | SMOTE objetivo 100% de mayoritaria; k=5 | 0,7645 | 0,8006 | 0,0360 | 0,1947 | 38,1493 |

En SMOTE, la referencia de la tabla es el control escalado **sin pesos**, no el candidato ponderado. Para comparar balanceo directamente:

- **Pacientes separados:** mejor SMOTE 0,4860; control ponderado sin historia 0,4491; diferencia SMOTE menos ponderado 0,0369.
- **Epochs mezclados:** mejor SMOTE 0,8006; control ponderado sin historia 0,7617; diferencia SMOTE menos ponderado 0,0388.

Las mayores medias observadas orientan selección, no prueban superioridad estadística ni un óptimo global.

## 4.6 · Diagnósticos

- **4.6.1:** importancia por permutación de los mejores RF/XGBoost base de ambos protocolos. Mide caída de F1 al desordenar variables en validación, cinco repeticiones/fold; promedio y dispersión entre folds. Se añadió la importancia del XGBoost final de 68 entradas, con cinco folds por pacientes y cinco repeticiones, más cuatro grupos conjuntos. No es correlación ni causalidad; la importancia conjunta no suma las individuales.
- **4.6.2:** matrices y métricas acumuladas del candidato elegido; no equivalen a promedios entre folds.
- **4.6.3:** ROC-AUC por etapa frente al resto. Se interpreta junto con precisión y recuperación, especialmente para clases minoritarias.
- **4.6.4:** resultados por paciente y cobertura. En epochs mezclados, las personas también aportan datos a entrenamiento; en pacientes separados, no.

Precision-Recall y solo wearable no forman parte del alcance activo de esta revisión; sus referencias históricas no se alteran.

### Qué mostró la importancia final

| Grupo permutado conjuntamente | Columnas | Caída media de F1 macro | Desviación entre folds |
| --- | --- | --- | --- |
| Actuales | 22 | 0,2306 | 0,0244 |
| Hace 1 minuto | 22 | 0,0476 | 0,0258 |
| Hace 2 minutos | 22 | 0,0218 | 0,0307 |
| Disponibilidad | 2 | 0,0006 | 0,0003 |

La mayor caída media correspondió al grupo **actuales** (0,2306). Los antecedentes de un minuto y dos minutos tuvieron caídas medias 0,0476 y 0,0218; describen dependencia del modelo, no una mejora garantizada al agregarlos. Los indicadores de disponibilidad tuvieron caída media 0,0006. Las desviaciones reflejan variación entre folds; no constituyen una prueba estadística de superioridad entre grupos.

La importancia conjunta se calcula permutando todas las columnas de un grupo con el mismo orden de filas y dejando las demás intactas. **No es la suma de importancias individuales ni un porcentaje causal**; los grupos tienen tamaños diferentes. La correlación puede repartir u ocultar información, y las permutaciones pueden generar combinaciones poco habituales. Una caída negativa no garantiza mejorar al quitar una entrada. Estos resultados no cambian columnas, parámetros ni candidatos.


## 4.7 · Comparación en los 16 pacientes reservados

Reentrena ambos candidatos con todo desarrollo, sin elegir usando test. Guarda pipelines y verifica serialización en desarrollo. Prepara las características del test según cada configuración, obtiene probabilidades una vez, persiste predicciones y luego calcula métricas. Los dos candidatos se evalúan sobre exactamente las mismas claves y etiquetas. Una comparación terminada se relee sin entrenamiento/inferencia; una incompleta se bloquea.

| Selección | Algoritmo | Pesos | Historia (min) | Entradas | F1 validación ± DE | F1 test | Exactitud test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pacientes separados | XGB | Sí | [1, 2] | 68 | 0,5053 ± 0,0265 | 0,5412 | 0,6126 |
| Epochs mezclados | RF | No | Sin historia | 22 | 0,8006 ± 0,0038 | 0,4985 | 0,6278 |

En los mismos 16 pacientes, el candidato seleccionado mediante **pacientes separados** obtuvo el mayor F1 macro. Diferencia epochs menos pacientes: **-0,0426**. Las validaciones no se comparan como si midieran generalización equivalente. La diferencia en test corresponde a estos candidatos concretos; pueden cambiar algoritmo, entradas y parámetros además del protocolo. No se realizaron reajustes posteriores.

## 4.8 · Evidencia histórica preservada

Conserva código, contadores y salidas del XGBoost anterior, con pesos e historia 1+2, 68 entradas; F1 macro histórico 0,5412. **No se ejecutó ni se modificó su código/salidas.** No es el resultado del candidato actual ni una tercera configuración seleccionada en esta ronda.

## 4.9 · Conclusiones y límites

Distingue selección en desarrollo, comparación actual de test y evidencia histórica. Informa errores por etapa y heterogeneidad entre pacientes. El test fue consultado históricamente y no se reajusta a partir de esta comparación.

## Cierre y continuidad

La ronda está terminada: selección, historia, SMOTE, comparación del test y nueva interpretación final. No se amplía la búsqueda de hiperparámetros ni se cambian candidatos a partir de las importancias.

Una evaluación externa con personas adicionales sería una posible ampliación futura y requeriría entradas compatibles y una muestra suficiente. No es un requisito pendiente para consultar o presentar esta ronda.
