# Resumen del notebook · Entrega 3

Guía de lectura de [temporal_version_tp_entrega03.ipynb](../../temporal_version_tp_entrega03.ipynb). Explica el recorrido desde los CSV preparados hasta la evaluación final. El objetivo es clasificar cada epoch de 30 segundos en W, N1, N2, N3 o REM (R), utilizando características de señales wearable y PSG.

La ronda de modelado y evaluación para personas nuevas está completa. Para interpretar las decisiones en mayor profundidad, consultar el [informe de modelado](informe-modelado.md); para parámetros, diferencias y conclusiones de cada prueba, la [guía de experimentos](experimentos-hiperparametros.md).

## 4.1 · Datos, test reservado y particiones

Carga los CSV `dataset_epochs_v1.csv` y `dataset_modelado_candidato.csv`, sin repetir EDA ni ETL. Comprueba alineación, claves únicas, entradas finitas y cobertura de las cinco etapas. Los identificadores, el tiempo y la etiqueta no entran como predictores.

Separa aproximadamente el 20 % de los pacientes con semilla 42 y conserva esa asignación para todos los experimentos:

| Conjunto | Pacientes | Epochs | Uso |
| --- | ---: | ---: | --- |
| Desarrollo | 60 | 45.011 | Entrenamiento, validación y selección |
| Test | 16 | 11.839 | Evaluación posterior a congelar el candidato |

Dentro de desarrollo prepara tres protocolos:

- **Pacientes separados:** cinco folds sin personas compartidas entre entrenamiento y validación. Responde cómo se comporta el modelo ante personas nuevas.
- **Epochs mezclados:** cinco folds estratificados que pueden compartir pacientes. Sirve como diagnóstico; compartir personas y observaciones próximas puede producir una estimación favorable para el objetivo de personas nuevas.
- **Cronológico por paciente:** seis bloques y cinco validaciones futuras con entrenamiento creciente y una separación de 15 minutos. Evalúa 37.490 epochs; los 7.521 del bloque inicial se conservan para entrenamiento. Supone pasado etiquetado disponible para entrenar sobre pacientes conocidos.

Todos predicen epochs. Lo que cambia es qué información pudo conocer el entrenamiento. Las tablas visibles resumen pacientes por fold; el detalle de cobertura se conserva en CSV.

## 4.2 · Configuraciones y reproducibilidad

Define los algoritmos y explica sus parámetros iniciales:

- **Dummy:** predice siempre la etapa mayoritaria del entrenamiento. Establece un piso de comparación.
- **Regresión logística:** referencia lineal multiclase, con estandarización aprendida dentro de cada entrenamiento.
- **Random Forest:** combina árboles para captar relaciones no lineales e interacciones.
- **XGBoost:** agrega árboles secuencialmente para reducir la pérdida del conjunto.

Fija semillas, opciones de ejecución y alternativas con/sin pesos. Estas configuraciones son referencias iniciales, no valores considerados óptimos de antemano.

## 4.3 · Evaluación común

Centraliza el entrenamiento y las métricas para que las comparaciones sigan las mismas reglas. Cada fold crea un pipeline nuevo; el preprocesamiento y los pesos se calculan únicamente con entrenamiento.

Guarda F1 macro de entrenamiento y validación, exactitud, precisión/recuperación/F1 por etapa, tiempos y probabilidades de validación. Cada epoch elegible recibe una predicción de validación por configuración, denominada OOF: se obtiene con el epoch fuera del entrenamiento de ese fold.

Las métricas se interpretan así:

- **Precisión:** proporción de detecciones de una etapa que son correctas.
- **Recuperación:** proporción de casos reales de esa etapa que se detectan.
- **F1:** combina precisión y recuperación mediante `2 × precisión × recuperación / (precisión + recuperación)`.
- **F1 macro:** promedio de los cinco F1 con igual peso. Es el criterio principal de selección.
- **Exactitud:** proporción total de aciertos; puede ocultar errores en etapas minoritarias si predomina N2.
- **Soporte:** cantidad real de casos de una etapa; no es una medida de calidad.
- **Brecha:** F1 de entrenamiento menos F1 de validación. Una brecha alta sugiere sobreajuste; reducirla sin mejorar validación no alcanza.

Los pesos balanceados son `N_entrenamiento / (5 × N_clase)`. Aumentan la penalización de errores en clases menos frecuentes, sin crear observaciones. Pueden mejorar recuperación y empeorar precisión. Validación y test se mantienen sin ponderar.

## 4.4 · Comparación controlada de protocolos

Ejecuta referencias con las mismas entradas e hiperparámetros, con y sin pesos, bajo los tres protocolos. Después de cada configuración presenta resultados por fold, promedio, desviación, brecha y métricas por etapa.

Un ejemplo decisivo es RF sin pesos: F1 macro **0,7617 con epochs mezclados**, frente a **0,3847 con pacientes separados**. El algoritmo no cambió; cambió la dificultad y la pregunta de evaluación.

En **4.4.4** se resumen resultados generales, tiempos y etapas por protocolo. Se conserva la mezcla como diagnóstico y se desarrollan candidatos independientes para personas nuevas y lecturas futuras de pacientes conocidos. No se elige el protocolo por su mayor cifra ni se consulta el test para decidir.

## 4.5 · Ajustes y experimentos

### 4.5.1 · Hiperparámetros

Prueba el catálogo de ajustes en ambos escenarios de selección. Se varía principalmente un parámetro por vez respecto de la referencia: regularización de logística, capacidad de RF y capacidad/regularización/muestreo de XGBoost.

La comparación permite observar si mejora F1 de validación, qué ocurre con las etapas, si aumenta la brecha y cuánto cuesta entrenar. No constituye una búsqueda exhaustiva de combinaciones. Una menor brecha puede acompañar un deterioro de predicción y no justifica por sí sola elegir un modelo.

### 4.5.2 · Representaciones de señales

Compara transformaciones `log1p` y canales combinados frente a separados, aislando los cambios. Busca determinar si importa cómo se representan las señales, manteniendo las fuentes intactas.

Separar canales mostró una pequeña ventaja para RF y deterioro para XGBoost en estas pruebas. Por eso la representación se selecciona por algoritmo y escenario, sin asumir una opción universalmente superior.

### 4.5.3 · Historia de señales anteriores

Sobre el mejor modelo base de cada escenario, mantiene los hiperparámetros y compara retardos de **1, 2, 5, 10 y 15 minutos**, la combinación **5+10** y la combinación de los dos mejores retardos individuales, **1+2 minutos**.

Utiliza señales pasadas del mismo paciente y segmento continuo, nunca etiquetas anteriores ni señales futuras. Una discontinuidad reinicia la historia. Cuando falta un antecedente, conserva el epoch con valores `NaN` y un indicador de disponibilidad; la imputación se aprende exclusivamente dentro del entrenamiento.

| Escenario | F1 macro sin historia | Con historia 1+2 minutos |
| --- | ---: | ---: |
| Personas nuevas | 0,4907 | **0,5053** |
| Pacientes conocidos: futuro | 0,5567 | **0,5803** |

Son medias de validación utilizadas para seleccionar candidatos. La combinación 1+2 obtuvo la mayor media observada; esto no demuestra que sea óptima para cualquier cohorte. Los indicadores también pueden aportar información sobre tiempo transcurrido y disponibilidad del registro.

### 4.5.4 · Pesos y SMOTE

Compara datos originales sin pesos, pesos balanceados y SMOTE sin pesos adicionales. Incluye un control escalado para distinguir el efecto del escalado del remuestreo.

SMOTE interpola observaciones minoritarias. Se probaron `k_neighbors=3/5` y cantidades objetivo por clase del 50/100 % de la mayoritaria, sin reducir clases. El escalado y el remuestreo se ajustan solo en entrenamiento; sus métricas se calculan sobre observaciones reales. Validación y test no reciben ejemplos sintéticos.

El mejor SMOTE obtuvo F1 macro aproximado **0,4860** para personas nuevas y **0,5639** para futuro de pacientes conocidos. Ninguno superó al candidato correspondiente con historia. Estas pruebas se hicieron **sin historia**: SMOTE+historia no se evaluó.

### 4.5.5 · Qué cambió y qué aprendimos

Reúne las conclusiones de ponderación, hiperparámetros, representaciones, contexto y balanceo. La guía documenta **147 comparaciones de desarrollo**, con referencias, diferencias, costos e interpretación.

Selecciona un candidato por escenario. La mayor media orienta la selección; diferencias pequeñas y desviaciones entre folds no prueban superioridad concluyente. Probar muchas variantes también puede sobreajustar la selección a validación.

## 4.6 · Diagnóstico de los modelos

### 4.6.1 · Importancia por permutación

Desordena una variable en validación y mide cuánto cae F1 macro. Repite cinco veces por fold y resume promedio y dispersión entre los cinco folds.

Una caída positiva mayor indica mayor dependencia del modelo respecto de esa variable. Una caída negativa significa que desordenarla mejoró el resultado observado; puede deberse a ruido o variabilidad. No mide causalidad ni un porcentaje explicado, y variables correlacionadas pueden compensarse.

**El análisis ejecutado corresponde a RF/XGBoost sin historia ni SMOTE. No representa todavía la importancia de las 68 entradas del modelo final.**

### 4.6.2 · Errores y matrices de confusión

Muestra las confusiones entre etapas y los reportes acumulados sobre predicciones OOF del candidato elegido por escenario. Permite identificar qué reconoce y dónde falla.

Estos resultados acumulados no son iguales al promedio entre folds. En el agregado por epoch, los registros largos tienen mayor peso.

### 4.6.3 · Precision-Recall y AP

Para cada etapa frente al resto, muestra recuperación en el eje horizontal y precisión en el vertical al variar el umbral. Permite observar cuánto aumentan las falsas alarmas al intentar detectar más casos.

La prevalencia funciona como referencia y Average Precision (AP) resume la curva. El punto de decisión por `argmax` representa la clasificación multiclase usada; las curvas no implican que se hayan ajustado umbrales.

### 4.6.4 · ROC y AUC

Relaciona recuperación con tasa de falsos positivos. Complementa PR, pero una ROC-AUC alta puede coexistir con baja precisión en una etapa minoritaria. Debe interpretarse junto con AP y métricas por etapa.

### 4.6.5 · Resultados por paciente

Muestra rendimiento individual y cobertura de etapas. Ayuda a detectar personas con malos resultados que el promedio puede ocultar.

Calcula F1 sobre cinco clases fijas; la ausencia de etapas limita comparaciones entre pacientes. En el escenario cronológico considera únicamente los períodos futuros elegibles.

## 4.7 · Solo wearable · pendiente

Deja planteado un modelo sin señales PSG, utilizando características de sensores portables. **No se ejecutó.** Los resultados actuales combinan wearable y PSG y no demuestran el rendimiento alcanzable únicamente con un dispositivo wearable.

## 4.8 · Congelación y evaluación final

Es un bloque independiente: puede ejecutarse desde un kernel limpio sin volver a entrenar los experimentos anteriores.

### 4.8.1 · Configuración congelada

Congela el candidato para personas nuevas antes de obtener resultados del test:

- XGBoost con pesos balanceados calculados en desarrollo.
- 200 rondas, profundidad 4, `learning_rate=0.1`, `reg_lambda=5`.
- `subsample=0.8`, `colsample_bytree=0.8` y semilla 42.
- 22 variables actuales + 22 de hace 1 minuto + 22 de hace 2 minutos + 2 indicadores: **68 entradas**.
- Imputación por medianas de desarrollo; cero para columnas completamente vacías. Sin escalado ni SMOTE.

Reentrena únicamente ese candidato con los 60 pacientes de desarrollo. Guarda configuración, fuentes, reglas, pipeline y modelo. El pipeline incluye imputador y clasificador; recibe las 68 entradas preparadas. La construcción de antecedentes se realiza antes, mediante las reglas del notebook.

Genera las probabilidades del test una vez y persiste las predicciones antes de calcular métricas. Las consultas posteriores verifican integridad y leen resultados sin reentrenar ni predecir. Una apertura incompleta se bloquea para conservar la evidencia.

### 4.8.2–4.8.6 · Resultados finales

Presenta por separado métricas globales y por etapa, matrices, Precision-Recall/AP, ROC-AUC y resultados de los 16 pacientes.

| Evaluación | F1 macro | Exactitud |
| --- | ---: | ---: |
| Validación por pacientes: media de cinco folds | 0,5053 | 0,6043 |
| Test: agregado de 16 pacientes y 11.839 epochs | **0,5412** | **0,6126** |

**N1 es la principal debilidad:** precisión 0,1733, recuperación 0,2958, F1 0,2185 y AP 0,1699. Aproximadamente el 82,7 % de las detecciones N1 son falsas. La exactitud global no permite afirmar buen reconocimiento de todas las etapas.

El F1 por paciente varía entre **0,1913 y 0,6369**, usando cinco clases fijas. Once de los 16 pacientes no presentan todas las etapas, lo que limita la comparación individual; aun así, hay heterogeneidad relevante.

### 4.8.7 · Evolución y comparación con validación

Conecta referencia, ajuste, historia y test, diferenciando sus condiciones. El F1 del test supera la media de validación en 0,0358, pero no demuestra una mejora del algoritmo: cambian los pacientes, la distribución y la cantidad utilizada para entrenar.

Las referencias históricas usaban 76 pacientes sin reserva interna. Sus resultados se conservan como antecedentes, no como comparaciones controladas con el desarrollo actual de 60 pacientes. Validación y test no se promedian ni se usan los resultados finales para reajustar.

## 4.9 · Conclusiones y límites

Conserva explícitamente las conclusiones previas a la apertura del test y agrega lo observado después. Las afirmaciones antiguas sobre un test cerrado describen ese estado histórico; el test actual ya está evaluado.

El candidato para personas nuevas queda congelado. Presenta capacidad predictiva desigual entre etapas y pacientes, con una debilidad marcada en N1. El test tuvo exposición histórica en EDA y comparaciones de la cohorte completa: no se presenta como históricamente intacto y no sustituye una evaluación externa.

Se conservaron los experimentos anteriores y el notebook `ANTERIOR`. La verificación registrada incluye 19 pruebas, controles de causalidad, separación, imputación, serialización, predicción única y relectura sin entrenamiento/inferencia.

## Trabajo pendiente y alternativas futuras

La ronda actual está cerrada. Las siguientes evaluaciones ampliarían la evidencia; los experimentos opcionales no son requisitos para darla por terminada. Ninguna nueva selección utilizará el test actual para ajustar parámetros, entradas o umbrales: requerirá evaluación independiente.

### Evaluaciones pendientes

**Pacientes externos.** Aplicar el pipeline congelado, sin reajustarlo, a personas adicionales con las mismas características y reglas de historia. Serviría para medir generalización fuera de la cohorte usada y reducir la limitación de exposición histórica del test interno. Requiere señales, etiquetas y procesamiento compatibles, suficientes pacientes y cobertura de etapas. Una muestra pequeña o muy distinta podría aportar evidencia limitada o evaluar un cambio de dominio más que la misma condición de uso.

**Prueba temporal independiente de pacientes conocidos.** Congelar el candidato cronológico y evaluarlo sobre períodos futuros que no hayan intervenido en selección, respetando continuidad, disponibilidad del pasado y separación temporal. Serviría para comprobar si el rendimiento de validación se mantiene al predecir lecturas posteriores. Si no existe un período reservado intacto, harán falta registros adicionales. Solo responde al escenario con pasado disponible; no demuestra generalización a personas desconocidas.

### Experimentos adicionales opcionales

**Solo wearable.** Entrenar un modelo independiente sin PSG y compararlo bajo las mismas particiones con una referencia comparable. Serviría para cuantificar qué se pierde al utilizar exclusivamente sensores portables y si ese rendimiento alcanza para el uso previsto. Puede empeorar la separación de etapas por retirar señales informativas; no se puede anticipar su utilidad a partir del resultado actual. Necesitaría su propia evaluación final independiente si se selecciona un nuevo candidato.

**Importancia del modelo con historia.** Calcular importancia por permutación sobre validación de la configuración de 68 entradas, ajustando cada modelo únicamente con su entrenamiento. Serviría para distinguir la dependencia de señales actuales, retardos e indicadores, que la importancia ya ejecutada no cubre. No implica una nueva medición de rendimiento en test. La correlación puede repartir u ocultar contribuciones: una importancia individual baja no demuestra que una señal o toda la historia sean prescindibles, ni prueba causalidad.

**Combinaciones de hiperparámetros.** Probar un conjunto acotado y declarado de combinaciones de ajustes prometedores, manteniendo entradas y folds. Ya se probaron variaciones individuales en validación; lo adicional sería investigar interacciones entre parámetros. Podrían mejorar el equilibrio entre capacidad y regularización, pero dos ajustes favorables por separado pueden perjudicarse al combinarse. Aumenta el costo y el riesgo de adaptar la selección a los mismos folds; no hay garantía de superar al candidato actual.

**SMOTE con historia · menor prioridad.** Comparar una referencia temporal sin pesos, otra ponderada y una variante con SMOTE sin pesos adicionales, manteniendo hiperparámetros y folds e incluyendo el control escalado. Ya se evaluaron SMOTE e historia por separado; esta combinación no se ejecutó. Podría modificar la detección de etapas minoritarias, pero no hay evidencia de mejora y SMOTE por separado no superó al candidato con historia. Además, interpolar puede producir relaciones poco plausibles entre señales actuales, antecedentes e indicadores; habría que definir un tratamiento que conserve la validez de estos últimos. Escalado y remuestreo permanecerían exclusivamente dentro de entrenamiento y se evaluarían observaciones reales.
