# Guía para explicar el notebook del TP de Ciencia de Datos

**Propósito:** explicar qué se estudia, por qué se hace y qué decisiones tomó el equipo. Sigue el orden de `temporal_version_tp_cdd.ipynb`. No es una explicación del código.

**Alcance de la entrega 2:** se presentan la comprensión de los datos, el análisis exploratorio y los avances del ETL (secciones 0–3). Las secciones 4–7 corresponden a **entregas posteriores**; no se espera entrenar ni evaluar modelos en esta entrega.

**Estado de las ejecuciones:** las salidas guardadas en esta versión corresponden a **77 archivos auditados**, **76 pacientes incluidos** y **56.850 epochs**. S027/S048 entraron parcialmente y S097 quedó excluido. La sección 3.8 del propio notebook todavía cita cifras de una corrida anterior; para la exposición se usan las salidas actuales de 3.1–3.2.

## 0. Contexto del proyecto

**Qué explicar:** buscamos clasificar `Sleep_Stage` en W, N1, N2, N3 y R a partir de señales fisiológicas. Es un problema de **aprendizaje supervisado**: hay señales de entrada y una etapa anotada como respuesta esperada. La salida es categórica, por eso la tarea futura es clasificación multiclase. Un CSV contiene muestras de un paciente a 100 Hz; 3000 muestras equivalen a 30 segundos.

**Por qué importa:** antes de analizar hay que definir la pregunta, la unidad de observación y el significado de la etiqueta. Las cinco etapas no deben tratarse como una escala numérica uniforme; REM no es «más profundo» que N3.

**Si preguntan por «ordinal»:** La clasificación de cinco clases, el equipo evita imponer un orden único porque R/REM no encaja en una escala de ordenamiento, como si sería por ejemplo: ALTO-MEDIO-BAJO. Elección de representación que conviene explicar.

* Fuente: `CD_01_Aprendizaje Automatico`, págs. 6–10 (aprendizaje supervisado y clasificación). La duración del epoch y las cinco etiquetas provienen del dataset y de la decisión del proyecto, no de esa presentación.

### 0.1. Librerías y configuración

Prepara herramientas de lectura, análisis y gráficos. No es una etapa analítica ni transforma datos. En la exposición basta decir que permite ejecutar el flujo de forma reproducible.

* Fuente: tema general de herramientas para Ciencia de Datos en `CD_01_Introduccion_Gestion_de_Proyectos`, págs. 52–60. La lista concreta de librerías es implementación del proyecto.

## 1. Carga de datos

### 1.1. Detección de archivos

Se localizan los CSV disponibles en el entorno y se comprueba cuántos pacientes pueden procesarse. La corrida guardada utiliza 77 archivos en Kaggle del dataset `dreamt-data`.

### 1.2. Paciente muestra

Se carga **un paciente completo** para conocer columnas, etiquetas y señales. Sirve para explorar el formato; no representa toda la cohorte. El procesamiento global aparece después.

* Fuente: `CD_02_02_ETLv2`, págs. 2–8 y 11–16 (fuentes y extracción). Elegir un paciente muestra es una decisión práctica del proyecto.

## 2. Análisis exploratorio de datos

El EDA busca **entender los registros y formular preguntas de calidad** antes de limpiar. Primero observa un paciente; luego audita todos los archivos. Sus gráficos describen datos, no prueban por sí solos que una señal prediga etapas ni que un extremo sea un error.

* Fuente: `CD_01_Introduccion_Gestion_de_Proyectos`, pág. 30 (comprensión y preparación de datos en CRISP-DM); `CD_02_03_Preprocesamiento`, págs. 7–16 (fuentes de problemas y pasos de preprocesamiento).

### 2.1. Dimensiones y tipos

Se comprueban filas, columnas y tipos. Una fila cruda equivale a una medición de 0,01 segundos; `Sleep_Stage` es categórica, las señales son numéricas y `TIMESTAMP` indica tiempo. Esto evita interpretar una columna con el tipo o la unidad equivocados.

* Fuente: `CD_02_03_Preprocesamiento`, págs. 2–6 (tipos de variables).

### 2.2. Variables categóricas y señales frente a etapa

#### 2.2.1. Frecuencia de las etapas

Se cuentan W, N1, N2, N3 y R en **los tres pacientes de la muestra exploratoria**, por separado y en conjunto, y se muestran sus porcentajes. Así vemos si una etapa domina o si alguna no aparece en uno de esos registros; todavía no describe a los 77 archivos.

#### 2.2.2. Señales frente a `Sleep_Stage`

Se dividen los registros de **esos mismos tres pacientes** en epochs de 30 segundos. Un **epoch puro** tiene una sola etapa válida durante toda la ventana. Se resumen señales como BVP y TEMP en cada epoch y se comparan con diagramas de caja, separados por paciente y etapa. Esto permite explorar diferencias y solapamientos sin mezclar las escalas de personas distintas. Los puntos extremos pueden ocultarse **en la figura** para leerla mejor; permanecen en los datos.

**Cómo leer la caja:** cada una representa los valores de una señal para una etapa de un paciente. La línea central es la mediana; la caja contiene la mitad central de los epochs y los bigotes muestran valores más alejados, hasta 1,5 veces el rango intercuartílico. Si las cajas de dos etapas están a distinta altura, sus valores centrales difieren; si se superponen mucho, esa señal por sí sola no las distingue claramente. Los puntos fuera de los bigotes son candidatos a revisión, no errores confirmados.

* Fuente: `CD_02_03_Preprocesamiento`, págs. 2–4 y 8–10 (variables categóricas, numéricas y valores irregulares). La elección de cajas por paciente y epochs puros es del proyecto.

### 2.3. Auditoría de valores nulos

Se auditan faltantes, infinitos y valores no numéricos en las señales de los pacientes exploratorios. El objetivo es saber si las columnas pueden analizarse como mediciones numéricas antes de decidir cualquier limpieza. No se modifican datos. Se excluyen las columnas de las apneas, ya que son otras etiquetas que el médico colocó (no es lo que buscamos predecir).

* Fuente: `CD_02_03_Preprocesamiento`, págs. 8–19 y `Class Notes/02 - Preprocesamiento.md` (faltantes e inconsistencias).

#### 2.3.1. Distribución e inspección de extremos

En el paciente muestra se resumen HR (frecuencia cardíaca estimada), TEMP, EDA (actividad electrodérmica) y SAO2 (saturación de oxígeno en sangre) con percentiles, mínimo y máximo. Luego se grafica cada señal durante los **30 segundos anteriores y posteriores** a su mínimo y a su máximo. Ver el entorno temporal ayuda a distinguir un pico aislado de un cambio sostenido o un posible problema de medición. **Un extremo es un caso para investigar, no una orden de eliminarlo**; esta sección no modifica datos ni describe a todos los pacientes.

* Fuente: `CD_02_03_Preprocesamiento`, págs. 8–10 y 21–22 (valores irregulares y limpieza). Los percentiles y la ventana temporal son herramientas elegidas por el equipo.

### 2.4. Epochs alineados del paciente muestra

Se buscan los cambios de etapa para ubicar dónde empiezan las ventanas completas de 3000 muestras (en desfasaje propio de los registros de cada paciente). Puede haber un fragmento inicial o final incompleto. Definir correctamente ventanas **antes de filtrar filas** conserva la correspondencia entre señal, tiempo y etiqueta.

* Fuente: tema de integración y transformación en `CD_02_03_Preprocesamiento`, págs. 23–29. La regla de 30 segundos y la inferencia del desplazamiento son específicas del dataset/proyecto; no están explicitadas en las filminas.

### 2.5. Evolución de etapas

El hipnograma muestra la secuencia de etapas del paciente a lo largo del tiempo; la matriz cuenta transiciones entre epochs consecutivos y confiables. Sirve para comprobar coherencia temporal y explicar que dormir es una **secuencia**, no solo una frecuencia global. Los epochs ambiguos se marcan para revisión.

* Fuente: tema de comprensión de datos en `CD_01_Introduccion_Gestion_de_Proyectos`, pág. 30. Hipnograma, transición y la regla de «revisar» son aplicaciones del dominio/proyecto, no una exigencia explícita de esas filminas.

### 2.6. Auditoría general de pacientes

Extiende la inspección a todos los CSV disponibles: estructura, lectura, continuidad temporal, etiquetas, faltantes, valores no numéricos y señales constantes. Guarda una auditoría para rastrear cada hallazgo. En la salida guardada se auditaron **77 archivos**, todos con lectura completa.

* Fuente: `CD_02_02_ETLv2`, págs. 11–18 (extracción y calidad antes de cargar); `CD_02_03_Preprocesamiento`, págs. 8–16 (errores e inconsistencias).

#### 2.6.1. Alineación y etiquetas faltantes

Se observa en qué fila cambia `Sleep_Stage`: si todos los cambios caen en límites de ventanas de 3000 muestras con el **mismo desplazamiento inicial**, se puede formar una única grilla de epochs de 30 segundos. La auditoría encontró **75 archivos con una alineación candidata consistente** y **dos con desplazamientos inconsistentes**, S027 y S048. «Candidata» significa que este control temporal resulta coherente, no que todas las etiquetas o señales sean perfectas.

En S027 y S048 los cambios siguen más de un desplazamiento, de modo que una sola grilla podría mezclar etapas dentro de un epoch. El ETL busca tramos continuos con alineación verificable y conserva solo esos epochs; deja fuera los tramos ambiguos. También se revisan etiquetas `Missing`. Detectar una inconsistencia no equivale a reparar automáticamente todo el registro.

* Fuente: tema de datos incompletos e inconsistentes en `CD_02_03_Preprocesamiento`, págs. 9–18. Las reglas concretas para pacientes y desplazamientos son decisiones del proyecto.

#### 2.6.2. SAO2

Se revisan rango, ceros y saltos. Un valor fuera de 0–1 solo viola ese rango **si la columna está expresada como fracción**; antes de convertir hay que confirmar la unidad. S027, por ejemplo, registra SAO2 casi constante alrededor de 12, distinto de la escala cercana a 0,9 observada en otros pacientes.

**Decisión:** el notebook no convierte ni corrige SAO2, ni excluye a S027 por esta señal. Conserva la columna en los CSV originales y deja SAO2 fuera de las características del ETL actual para **todos** los pacientes. Así se evita incorporar una medición cuya escala y calidad todavía no están confirmadas; revisarla queda pendiente si se quiere usar más adelante.

* Fuente: tema de inconsistencias y validación de variables en `CD_02_03_Preprocesamiento`, págs. 10–16. El rango y la exclusión temporal de SAO2 son decisiones del proyecto.

#### 2.6.3. Señales constantes

Una señal puede no tener nulos y, aun así, aportar poca información si queda plana durante mucho tiempo. La auditoría detectó **18 señales completamente constantes en S097**; por sus múltiples señales PSG planas, el ETL lo excluyó provisionalmente. Otros pacientes tienen IBI constante, pero no se excluyen por eso.

* Fuente: tema de datos con ruido/inconsistentes en `CD_02_03_Preprocesamiento`, págs. 12–16. El criterio para S097 es específico del proyecto.

#### 2.6.4. EDA

Se comparan máximos entre los 77 archivos y se revisan trayectorias crudas de S002, S004 y S057, junto con señales de movimiento. Un máximo aislado no informa duración ni causa; todavía no justifica recorte o eliminación.

* Fuente: tema de valores irregulares y limpieza en `CD_02_03_Preprocesamiento`, págs. 8–10 y 21–22. La inspección de EDA y ACC es específica del dataset.

## 3. Preparación y evaluación del dataset de epochs

El ETL cambia la unidad de análisis: de miles de muestras por paciente a **una fila por paciente y epoch completo de 30 segundos**. Así cada observación tiene una etiqueta y resúmenes comparables de señales. Los CSV originales se conservan.

Las anotaciones de apnea (`Obstructive_Apnea`, `Central_Apnea`, `Hypopnea`, `Multiple_Events`) quedan en los CSV originales y **no entran en `dataset_epochs_v1.csv`**. Las señales respiratorias medidas (`PTAF`, `FLOW`, `THORAX`, `ABDOMEN`, `SNORE`) sí se resumen por epoch. Una anotación clínica y una medición fisiológica cumplen funciones distintas.

* Fuente: `CD_02_02_ETLv2`, págs. 11–16 (extraer, transformar y cargar); `CD_02_03_Preprocesamiento`, págs. 23–29 (integración y agregación). La unidad «epoch» pertenece al problema.

### 3.1. Construcción del dataset

Se verifica continuidad y alineación; se resumen señales con medidas de centro, variación y cobertura. Entran epochs completos con etapa válida y pura. Solo se completa una etiqueta `Missing` aislada si los dos vecinos confiables tienen la misma etapa; se marca como **inferida**. Tramos ambiguos quedan fuera del dataset supervisado y registrados. S027/S048 aportaron solo segmentos verificables; S097 quedó excluido provisionalmente.

* Fuente: `CD_02_03_Preprocesamiento`, págs. 17–19 y 23–29 (alternativas ante faltantes, integración, agregación). La regla de vecinos, alineación y exclusiones son decisiones del proyecto, no recetas de la cátedra.

### 3.2. Resumen posterior al ETL

Concilia cuántos pacientes y epochs entraron, cuáles se descartaron y qué etiquetas se infirieron. `dataset_epochs_v1.csv` contiene la tabla; `auditoria_epochs.csv` y `epochs_descartados.csv` explican cómo se llegó a ella. El manifiesto permite reutilizar resultados cuando fuentes y reglas coinciden. La salida guardada informa **77 archivos auditados, 76 pacientes incluidos (74 completos y 2 parciales), 56.850 epochs**, tres etiquetas imputadas y ningún epoch descartado por pureza.

* Fuente: `CD_02_02_ETLv2`, págs. 14–18 (transformación, carga y calidad). Archivos de auditoría, manifiesto y reglas de conciliación son prácticas del proyecto.

### 3.3. Distribución de etapas, señales y atípicos

Se compara la frecuencia de las cinco clases y las características resumidas por epoch. En los **76 pacientes incluidos**, N2 fue la etapa más frecuente (51,96 %) y N3 la menos frecuente (3,87 %). Las cajas por etapa muestran cuánto se solapan las señales; no prueban por sí solas que permitan clasificar pacientes nuevos.

#### 3.3.1. Revisión exploratoria de valores atípicos

El criterio global 1,5 × IQR **marca epochs para revisar**, no define límites fisiológicos ni elimina datos. Se observa si los casos se concentran en ciertos pacientes o forman tramos consecutivos; la distancia en IQR sirve para ordenar casos **dentro de una señal**. Las cajas de 3.3 calculan cuartiles por etapa y, por eso, pueden marcar otros puntos.

IQR es el **rango intercuartílico**: la distancia entre los percentiles 25 y 75, donde se concentra la mitad central de los valores. Un epoch que queda a más de 1,5 veces esa distancia por debajo o por encima de ese rango se señala como atípico para investigarlo, no como medición necesariamente errónea.

#### 3.3.2. Distribuciones de predictores prioritarios

Se comparan histogramas y cajas por etapa de resúmenes **por epoch**: medianas para HR, TEMP y EDA; dispersión para BVP, aceleración y una señal PSG. También se mira una vista **cruda a 100 Hz de un solo paciente** para reconocer picos y movimiento. Una muestra cruda no es un epoch independiente ni representa a toda la cohorte. Ocultar puntos extremos en una figura no los borra del dataset.

#### 3.3.3. EDA en todos los pacientes incluidos

Se comparan mediana y percentiles de EDA por paciente y se observa su evolución temporal en los epochs conservados. Esto ayuda a distinguir un nivel habitualmente alto de episodios localizados; los espacios sin epochs retenidos no prueban que falte EDA cruda. `log1p` facilita **solo la visualización**. S004/S057 requieren contrastar estos resúmenes con sus señales crudas antes de decidir un tratamiento.

«Pendiente de revisión» significa que S004 y S057 están marcados para investigar, no descartados: sus medianas de EDA son bajas (0,322 y 0,244), pero sus percentiles 95 llegan a 45,269 y 6,069. El mapa de evolución muestra, por paciente y por bloques de cinco minutos, la mediana de EDA de los epochs conservados. Permite ubicar cuándo aparecen valores altos; un hueco indica que en ese bloque no hubo epochs conservados para graficar, no necesariamente que faltara la señal original.

* Fuente: `CD_02_03_Preprocesamiento`, págs. 8–10, 17–22 (outliers y limpieza). Mediana, desviación e IQR son herramientas estadísticas aplicadas por el proyecto; el tratamiento específico no está impuesto en las filminas.

### 3.4. Asociación entre señales y etapas

Estas asociaciones son descriptivas: no demuestran causalidad, utilidad conjunta ni desempeño en pacientes nuevos. `Sleep_Stage` no se convierte en una escala numérica ordinal.

#### 3.4.1. Asociación entre predictores

Spearman compara **señales entre sí** para detectar información similar. Una correlación alta sugiere revisar redundancia y cobertura; no obliga a quitar una columna ni indica que esa señal prediga la etapa.

Spearman es el **coeficiente de correlación** que resume si dos variables tienden a subir o bajar juntas: va de −1 a +1, y cerca de 0 indica poca asociación monotónica. El mapa de calor es solo la forma de representar esos coeficientes mediante colores; por ejemplo, C4-M1_std y F4-M1_std alcanzan 0,936 en esta corrida.

#### 3.4.2. Asociación con cada etapa

La AUC de rangos compara una etapa frente a las otras cuatro para ver si los valores de una señal tienden a ser mayores o menores en esa etapa. Se transforma a una escala donde **0 significa sin separación por rangos**; el signo indica dirección. La tabla informa cuántos epochs y pacientes sostienen cada comparación. No es rendimiento de un modelo fuera de muestra.

En el mapa, **rojo no indica un error**: un valor positivo señala que la característica suele ser mayor en esa etapa que en el resto; uno negativo señala que suele ser menor. Por ejemplo, +0,7 en N3 equivale a una AUC de rangos de 0,85 para esa comparación descriptiva, no a un 70 % de acierto. Como N3 aparece en menos pacientes, esa diferencia debe comprobarse luego con una evaluación separada por paciente.

* Fuente: tema de variables relacionadas/multicolinealidad en `CD_04_01_RegresionLineal`, pág. 37, y preparación de datos en `CD_01_Introduccion_Gestion_de_Proyectos`, pág. 30. Spearman y AUC de rangos no aparecen como procedimiento obligatorio en esas filminas; son elecciones exploratorias del proyecto.

#### 3.4.3. Relación entre tiempo y etapa

Se usa `tiempo_relativo_segundos`, contado desde el inicio del CSV, para analizar todos los epochs evaluables del ETL cargado. Las cajas muestran cuándo aparecen las etapas; la AUC de rangos global y por paciente describe si una etapa tiende a aparecer antes o después que el resto. AUC cercana a 0,5 no descarta patrones cíclicos. Las proporciones por bloques de 30 minutos se comparan con peso por epoch y con igual peso por paciente observado, junto con la cobertura. Los huecos no se rellenan y los pacientes sin suficientes epochs para una etapa quedan no evaluables. Los controles permanecen dentro del notebook. No se entrenan algoritmos ni se incorpora el tiempo a `X`: su utilidad se evaluará después con pacientes separados.

### 3.5. Revisión y variantes de características

Se revisa qué características existen, cómo se comportan y qué alternativas podrían probarse después. Las columnas originales permanecen en el dataset base.

#### 3.5.1. Ficha de variables y consistencia entre pacientes

Se resumen cobertura, variación y marcas de revisión de cada característica. Después se observa si las diferencias entre etapas mantienen su **dirección** en distintos pacientes, en vez de depender solo de la mezcla global. Es un filtro exploratorio para formular hipótesis, no una selección definitiva.

En esta corrida, la mediana de HR y la variabilidad de BVP son mayores en vigilia que en las otras etapas para aproximadamente el 85 % de los pacientes evaluables; la variabilidad de ACC_X muestra la misma dirección en el 97 %. En cambio, la mediana de EDA no muestra una dirección consistente. Para N3 solo hay 27 pacientes con suficientes epochs para esta comparación, así que sus resultados requieren más cautela. Estas observaciones orientan qué características probar después, pero todavía no demuestran capacidad predictiva en pacientes nuevos.

#### 3.5.2. Variantes reversibles de características

Se definen **14 alternativas** para PSG + wearable y wearable solo: `log1p` en colas no negativas, máximos bilaterales para ojos o piernas, resumen de aceleración y variantes que omiten un canal EEG **solo en la copia candidata**. Sirven para comparar representaciones; no corrigen mediciones ni modifican el ETL base.

#### 3.5.3. Control descriptivo de variantes

Se comprueba que cada alternativa conserve los mismos epochs e índice y produzca valores finitos; también se registra qué columnas entran o salen de cada conjunto `X`. Pasar estos controles significa que la variante **se puede construir**, no que clasifique mejor. Aquí no se entrena ningún algoritmo.

* Fuente: `CD_02_03_Preprocesamiento`, págs. 24–35 (transformación y reducción). Las fórmulas y comparaciones concretas son propuestas del proyecto.

### 3.6. Variación entre pacientes

Se comparan proporciones de etapas y duración válida por paciente. Una proporción global puede estar dominada por registros largos; mirar pacientes individualmente muestra heterogeneidad y ayuda a interpretar clases poco frecuentes. Una etapa ausente significa «no observada en los epochs conservados», no que esa persona no pueda alcanzarla.

* Fuente: tema de comprensión/evaluación de datos en `CD_01_Introduccion_Gestion_de_Proyectos`, pág. 30. Los resúmenes por paciente y su interpretación no están prescriptos explícitamente en las presentaciones.

### 3.7. Controles lógicos de rangos

Se comprueba que recuentos estén entre 0 y 3000, fracciones entre 0 y 1 y desviaciones estándar no sean negativas. También se revisa la coherencia entre cobertura y faltantes. Una infracción dispara inspección de la fuente; esta sección **no corrige ni recorta** datos.

* Fuente: `CD_02_03_Preprocesamiento`, págs. 11–16 y 22 (datos inconsistentes y detección). Los límites lógicos particulares se derivan del significado de las columnas.

### 3.8. Estado de la entrega ETL

Separa lo **hecho** de lo que falta verificar **dentro de la entrega 2**: dataset, auditoría y marcas de calidad de la cohorte actual. **El texto de 3.8 en el notebook aún dice 74 archivos, 73 pacientes y 54.367 epochs; sus salidas actuales muestran 77, 76 y 56.850.** Las tres etiquetas imputadas sí coinciden. El entrenamiento de modelos pertenece a entregas posteriores.

* Fuente: `CD_01_Introduccion_Gestion_de_Proyectos`, pág. 30 (fases y evaluación de CRISP-DM). El estado y los recuentos son evidencia del proyecto.

### 3.9. Tabla candidata para modelado

Se materializa **una** de las representaciones candidatas, manteniendo intacto el dataset ETL base. Es una alternativa técnica, no una prueba de que esas variables clasifiquen mejor.

#### 3.9.1. Copia candidata y columnas fuera de `X`

Se aplican `log1p` a BVP, EDA mediana y dispersión de ACC, y máximos bilaterales a ojos y piernas. La copia conserva identificadores, tiempo y etiqueta para trazabilidad, pero quedan fuera de `X`. Las columnas sustituidas permanecen en el ETL base; las exclusiones son solo de esta propuesta de predictores.

#### 3.9.2. Controles y exportación

Antes de exportar `dataset_modelado_candidato.csv`, se comprueba que sigan iguales los epochs, las claves y las clases, que los predictores sean finitos y que el ETL base no haya cambiado. Superar esas pruebas valida la **construcción técnica**, no su utilidad predictiva.

* Fuente: `CD_02_03_Preprocesamiento`, págs. 24–35 (transformación y reducción); `CD_01_Aprendizaje Automatico`, págs. 17–21 (entradas y salida supervisada). La selección exacta de columnas es una decisión provisional del proyecto.

## 4–7. Algoritmos, resultados, interpretación y conclusiones

Estas secciones son **espacios reservados para próximas entregas**. En la exposición de la entrega 2 basta aclarar que aún no corresponde presentar modelos, métricas predictivas ni conclusiones sobre su rendimiento. Más adelante habrá que definir el escenario (PSG + wearable o wearable solo) y evaluar con separación por paciente.

* Fuente: `CD_01_Aprendizaje Automatico`, págs. 6–10 y 17–21 (aprendizaje supervisado); `CD_01_Introduccion_Gestion_de_Proyectos`, pág. 30 (modelado y evaluación). La partición por paciente y las métricas propuestas son decisiones metodológicas del proyecto; las filminas vistas no las establecen como requisito específico para este TP.

## Guion oral breve

1. **Problema:** «Queremos clasificar cinco etapas de sueño a partir de señales; por eso la salida es categórica y el futuro modelo será supervisado».
2. **Comprensión:** «Primero verificamos qué representa una fila, cómo están anotadas las etapas y si hay faltantes o incoherencias; no limpiamos a ciegas».
3. **Decisión central del ETL:** «Agrupamos 3000 muestras en un epoch de 30 segundos, solo cuando tiempo y etiqueta quedan alineados. Conservamos trazabilidad de lo descartado y de las pocas etiquetas inferidas».
4. **Análisis del dataset resultante:** «Revisamos desbalance, distribuciones, extremos, asociaciones y diferencias entre pacientes. Es evidencia descriptiva para decidir qué probar después».
5. **Cierre de la entrega 2:** «Las variantes de características son candidatas; el modelado corresponde a entregas futuras. La corrida actual auditó 77 archivos y produjo 56.850 epochs de 76 pacientes incluidos, con exclusiones e imputaciones registradas».

## Tres preguntas previsibles

- **¿Por qué no borrar todos los outliers?** Una marca estadística no identifica por sí sola un sensor defectuoso. Primero se revisan unidad, señal cruda y contexto temporal; si se confirma un problema, se documenta una regla específica.
- **¿Por qué no usar todos los epochs?** Un epoch sin etiqueta confiable puede enseñar una relación errónea. Se conserva el origen y se audita el descarte; solo se usan etiquetas inferidas bajo una regla muy restringida y marcada.
- **¿Por qué separar por paciente al modelar?** Epochs vecinos de la misma persona están relacionados. Separar filas al azar podría poner señales del mismo paciente en entrenamiento y prueba y exagerar el desempeño en personas nuevas.

**Material consultado:** PDFs de `Presentations/`, notas de `Class Notes/`, notebook local y `docs/` de este repositorio. Las páginas indicadas corresponden a los PDFs, no a los números de sección del notebook. Ante diferencias entre una nota informal y una filmina, se priorizó la filmina y se explicitó cuándo una regla es propia del proyecto.
