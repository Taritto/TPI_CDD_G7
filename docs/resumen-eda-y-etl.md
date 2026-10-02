# Resumen del EDA y del ETL de etapas del sueño

**Lectura actualizada del notebook adjunto:** este documento incluye una revisión exhaustiva en el apartado **E**, una guía de variables y transformaciones en **F–G**, y prioridades para continuar en **H–J**. Los apartados A–D conservan el contexto del trabajo y la verificación anterior. La revisión actual identifica salidas de distintas ejecuciones y un defecto temporal en 3.6; por eso no certifica una corrida integral de la cohorte amplia ni una selección predictiva final.

**Para discusión del equipo.** Fuente de trabajo: CSV por paciente de DREAMT 2.2.0 y [notebook principal](../temporal_version_tp_cdd.ipynb). Objetivo: construir una tabla supervisada para clasificar `Sleep_Stage` en **W, N1, N2, N3 y R** usando señales de PSG y wearable. El registro está a 100 Hz; un epoch de 30 segundos reúne 3000 filas crudas. **La etapa es categórica:** REM no es un nivel más profundo que N3.

**Alcance de los resultados:** las salidas históricas guardadas del notebook muestran **74 archivos auditados, 73 incluidos** (71 completos y 2 parciales), S097 excluido y **54.367 epochs**. La ejecución vigente procesa los archivos disponibles y calcula sus propios recuentos en 3.1–3.2 y 3.9.3; las cifras históricas no fijan el tamaño del dataset actual. Antes de modelar, conservar juntos el dataset, las auditorías y el manifiesto de la misma ejecución, y verificar sus controles.

## A. EDA inicial: comprender los CSV, sin limpiar

| Secciones | Qué hacen | Para qué sirve / límite |
| :--- | :--- | :--- |
| 1 y 2.1 | Localizan los CSV, cargan un paciente muestra y revisan columnas, tipos, tamaño y tiempos. | Entender la fila cruda (una muestra a 100 Hz); no representa por sí sola a toda la cohorte. |
| 2.2–2.2.2 | Cuentan etapas y comparan señales resumidas por epochs puros en pocos pacientes. | Describir desbalance y posibles relaciones; cajas y puntos extremos no son reglas de eliminación. |
| 2.3–2.3.1 | Auditan nulos, rangos y contexto temporal de mínimos/máximos del paciente muestra. | Detectar casos a revisar sin alterar datos. |
| 2.4–2.5 | Comprueban alineación de ventanas de 3000 muestras, transiciones e hipnograma del paciente muestra. | Ver secuencia sueño–tiempo; un hipnograma individual no prueba una asociación para todos los pacientes. |
| 2.6–2.6.4 | Auditan todos los archivos disponibles por bloques; revisan alineación S027/S048, etiquetas `Missing`, escala de SAO2, señales constantes y EDA. La auditoría se reutiliza si coinciden fuentes y reglas. | Priorizar incidencias; los CSV fuente permanecen intactos. El gráfico global de máximos EDA incluye archivos auditados, no necesariamente solo pacientes incluidos. |

**Hallazgos EDA relevantes:** S097 presenta múltiples señales PSG constantes; S027/S048 tienen segmentos desalineados; SAO2 e IBI requieren revisión antes de incorporarse como características. S004 tiene un aumento prolongado de EDA y S057 una subida y descenso pronunciados. El gráfico nuevo de máximos EDA usa `log1p` **solo para visualizar** y marca S004/S057 en rojo manualmente; no demuestra error ni transforma el dataset. Un máximo no informa duración ni nivel basal. También hay TEMP baja en algunos pacientes. Ninguno de esos casos autoriza por sí solo borrar pacientes o recortar valores.

## B. ETL: de muestras crudas a una fila por epoch

| Secciones | Implementación existente | Resultado |
| :--- | :--- | :--- |
| 3.1 | Verifica continuidad y fase de las anotaciones; define ventanas completas de 30 segundos **antes de filtrar filas**. Resume 24 señales por epoch con media, desviación estándar, mediana, recuento válido y fracción faltante. | `dataset_epochs_v1.csv`: una fila por `patient_id` + `epoch`, con `Sleep_Stage`, `TIMESTAMP`, `tiempo_relativo_segundos`, resúmenes y marcas de calidad. |
| 3.1–3.2 | Conserva solo epochs completos de etapa válida y pura. Imputa **solo la etiqueta de trabajo** de un `Missing` aislado con vecinos puros, contiguos e iguales; marca `etiqueta_imputada` y pureza original. Excluye tramos largos o ambiguos sin rellenar. Recupera únicamente segmentos verificables de S027/S048 y mantiene S097 excluido provisionalmente. | `auditoria_epochs.csv` y `epochs_descartados.csv` permiten rastrear inclusiones, exclusiones e imputaciones. S089/S095/S096 aportaron una imputación aislada cada uno en la ejecución informada. |
| 3.1 | Usa un manifiesto de fuentes y reglas para cargar CSV cacheados si coinciden; el recálculo completo es explícito. | Evita repetir la lectura costosa de los archivos crudos cuando la caché es válida. En Kaggle debe recuperarse la salida tras una sesión nueva. |
| 3.3–3.3.3 | Describe proporciones de etapas, distribuciones por epoch, candidatos IQR y EDA por paciente y tiempo. En 3.3.2 añade cajas y un tramo de señales crudas del paciente de muestra ya cargado. | La vista cruda es individual, no de los 73 pacientes; ayuda a ver picos y ruido sin confundir muestras a 100 Hz con epochs. **No** aplica clipping, binning ni eliminación automática. |
| 3.4–3.4.3 | Calcula Spearman entre predictores, asociación univariada con etapas y relación descriptiva tiempo–etapa usando `tiempo_relativo_segundos`: distribuciones, AUC global y por paciente, proporciones por bloques de 30 minutos y cobertura. La prueba temporal incluye controles en el notebook y no comprime huecos ni modifica el ETL. | Prioriza preguntas para modelado; no demuestra causalidad ni rendimiento en pacientes nuevos. Ejecutar con la cohorte objetivo e interpretar resultados y tamaños; AUC temporal cercana a 0,5 no descarta un patrón cíclico. |
| 3.5–3.5.3 | Informa cobertura y diferencias dentro de pacientes; define 14 representaciones (`log1p`, ojos, piernas, ACC, candidata combinada y ablaciones EEG) y comprueba descriptivamente columnas, cantidad de epochs, índice y finitud. | Esta versión **no ejecuta regresión logística ni otro algoritmo**; la anterior sí incluía una celda de entrenamiento, sin salida guardada. Pasar controles no prueba utilidad predictiva. Ningún canal queda anulado automáticamente. |
| 3.6–3.8 | Resume etapas, REM y transiciones por paciente; controla rangos lógicos; documenta decisiones y pendientes. | Las proporciones y duración válida son interpretables. **3.6 necesita corregir latencias, tramo observado y continuidad para usar tiempo real**, no el número de epoch entre segmentos recuperados. La sección 4 lista algoritmos posibles, sin entrenamiento. |
| 3.9 | Materializa en memoria una copia candidata con reducciones ojos/piernas/ACC y `log1p` de BVP, EDA mediana y norma ACC; registra el estado de todas las columnas, compara distribuciones y clases, ejecuta doce controles **dentro del notebook** y recién entonces exporta `dataset_modelado_candidato.csv`. En 3.9.3 muestra las claves y recuentos por CSV y paciente, con pruebas de rechazo de duplicados y reexportación. | No altera el ETL base. La copia no es una selección final ni aplica imputación de señales, binning, clipping o balanceo; su rendimiento se evaluará recién en la etapa de algoritmos de la sección 4. |

**Clases en la ejecución amplia informada:** W 12.047 (22,2 %), N1 6.389 (11,8 %), N2 28.020 (51,5 %), N3 2.059 (3,8 %) y R 5.852 (10,8 %). N3 apareció en 35 pacientes y R en 61. El desbalance se **conserva** en el dataset; sus efectos se tratarán al evaluar modelos, no fabricando filas en el ETL.

**S027 y S048 en el mapa de EDA:** ambos aportan dos segmentos recuperados. S027 conserva 532 epochs y deja 680.900 filas crudas fuera por alineación; S048 conserva 677 y deja 389.900 fuera. En los epochs incluidos, `EDA_median` es finita en **532/532** y **677/677**, respectivamente; los 73 pacientes muestran cobertura EDA de 100 % dentro del dataset final. El mapa divide `tiempo_relativo_segundos` en bloques de cinco minutos y deja en blanco los bloques **sin epochs conservados** (también el tiempo posterior al fin de cada registro). Por eso sus blancos no prueban EDA faltante: reflejan, principalmente, la selección temporal del ETL. La auditoría cruda guardada de 2.6 informa cero nulos, infinitos y valores no numéricos en las señales de los 74 archivos, incluidos ambos pacientes. Eso no prueba calidad instrumental. Falta conciliar explícitamente los bloques con los intervalos recuperados/excluidos; E.6 detalla la diferencia. No interpolar epochs ni etiquetas a través de estos huecos. El nivel EDA relativamente alto de S027 (mediana por epoch 5,225 µS; p99 30,502) merece inspección de escala/calidad, pero no es por sí mismo un error.

**Fuera de las características actuales:** SAO2 e IBI por disponibilidad/calidad no resuelta; anotaciones de apnea porque son eventos clínicos y no predictores principales. Se conservan en el origen. No hay recorte global de extremos ni interpolación automática de señales. Los metadatos de pureza, cobertura e imputación se mantienen para auditoría; no se proponen como predictores iniciales.

### Identidad de las filas y repetición del paciente

El dataset base y el candidato tienen **una fila por epoch**, identificada por `(patient_id, epoch)`. El ID de un paciente aparece tantas veces como epochs válidos aporta; esto conserva su secuencia de señales y etiquetas. La sección 3.9.3 informa por paciente las filas, los epochs y los instantes distintos, y comprueba que sus recuentos coincidan con el ETL base. Las pruebas registradas verifican que reexportar reemplaza el CSV sin acumular filas y que una clave duplicada se rechaza antes de sobrescribir una salida válida. Los tamaños y resultados corresponden a los archivos procesados en cada ejecución.

La sección 0.2 declara las claves de los 14 tipos de CSV: paciente/archivo, archivo + señal, cambio de etapa, tramo o motivo de revisión según la salida. Cada exportación y carga de caché comprueba su clave; las tablas de epochs también exigen un instante único por paciente. Una clave faltante o repetida bloquea la escritura con ejemplos para revisar el origen. La sección 3.9.3 registra las pruebas y muestra filas y epochs distintos por paciente. No se elimina por `patient_id`: eso borraría observaciones temporales legítimas. Las versiones base y candidata representan los mismos epochs y no deben concatenarse verticalmente como si fueran observaciones nuevas.

## C. Qué está cerrado y qué falta

| Estado | Decisión o tarea |
| :--- | :--- |
| **Hecho** | Existe la transformación crudo → epochs de 30 segundos, un dataset consolidado, caché, trazabilidad de descartes, reglas de imputación aislada y recuperación parcial documentada. EDA, atípicos, clases y asociaciones tienen análisis descriptivo. |
| **Comprobado en las salidas guardadas de 73 pacientes** | Las clases suman 54.367; 3.5.1 resume diferencias dentro de pacientes; 3.6 informa 12 sin R y 38 sin N3 observados; 3.7 informa **sin violaciones** de reglas lógicas y 54.367 valores finitos para las variables mostradas. Esto no certifica la calidad instrumental; los cálculos temporales de 3.6 requieren corrección y el CSV amplio debe conservarse para reproducir los resultados. |
| **Verificar / ejecutar** | Conciliar bloques vacíos de S027/S048; corregir el uso de `epoch` como reloj en 3.6 y como continuidad en 3.3.1; revisar escalas de FLOW y otros canales. Ejecutar vista cruda, prueba temporal, variantes y candidato con una misma cohorte, sin aceptar reducciones ni tiempo por controles estructurales. Repetir redundancia/dominio detallados y evaluar fuera de paciente antes de elegir columnas. |
| **Revisión dirigida, sin limpieza aprobada** | Decidir si EDA S004/S057 y TEMP baja son variación plausible o fallas localizadas; contrastar señal cruda, duración, unidades y cobertura. Si no se confirma defecto, conservar con marca. |
| **Pendiente de modelado** | Implementar recién en la sección 4 la reserva de pacientes de prueba, referencias triviales y modelos candidatos. Comparar PSG + wearable frente a wearable solo según el objetivo, y luego señales/tiempo/señales + tiempo y ponderación de clases solo en entrenamiento. No hay métricas predictivas guardadas ni selección final. |

**Acuerdo recomendado para el equipo:** conservar íntegro el dataset base y documentar cualquier corrección de fuente; retirar columnas únicamente de una copia de modelado y después de una comparación por paciente. El [plan ejecutable](plan-ejecucion-transformacion.md) prioriza los controles aún abiertos y las pruebas de transformación. El control 3.7 ya tiene salida guardada completa; la selección de predictores sigue **provisional**.

## D. Prueba temporal y verificación de ejecución — 01/10/2026

La nueva **3.4.3** usa `tiempo_relativo_segundos`, no el número de epoch, para comparar etapas. Incluye distribuciones temporales, AUC de rangos global y por paciente, proporciones por bloques de 30 minutos y cobertura. Mantiene los huecos reales y diferencia el peso por epoch del peso igual por paciente. Sus tablas y gráficos quedaron guardados en el notebook; no se entrenó ningún algoritmo ni se incorporó el tiempo a `X`.

La ejecución secuencial de las **39 celdas de código no vacías** terminó sin excepciones en **451,7 segundos**, con **28 figuras renderizadas**. Se procesaron íntegramente los **18 archivos fuente disponibles** y se cargó la caché de **13.165 epochs** en 3.1. Se ejecutó el código en un mismo espacio de Python, redirigiendo únicamente las rutas de salida a una carpeta temporal y copiando allí la caché. Los hashes de los CSV originales quedaron idénticos.

- **Controles aprobados dentro del notebook:** 15 temporales (3.4.3), 12 de transformación (3.9.2) y 9 de identidad/exportación (3.9.3).
- **Error encontrado y corregido:** el validador de 0.2 intentaba detectar filas idénticas mediante `duplicated()` sobre auditorías con columnas que contienen listas. Ahora informa cero filas idénticas después de exigir una clave única, que ya impide duplicar una fila completa. Dos controles de regresión en 3.9.3 verifican que las listas no causen errores y que las claves repetidas sigan rechazándose.
- **Límite de la verificación:** valida el recorrido con caché existente y los archivos disponibles, no la reconstrucción completa de epochs desde cero ni la cohorte ampliada de Kaggle. S077 no estaba entre las fuentes disponibles; su incidencia histórica de alineación no queda resuelta ni verificada por esta corrida.

En esta ejecución, R aparece relativamente más tarde (AUC global **0,633**; mediana dentro de pacientes **0,673**) y N3 más temprano (**0,310** y **0,260**, respectivamente). Para N3 solo **5 pacientes** cumplieron el mínimo de cinco epochs de la etapa y cinco del resto. Son resultados descriptivos de esta ejecución, no una regla clínica ni una validación predictiva. La comparación futura señales/tiempo/señales + tiempo sigue pendiente con separación por paciente.

## E. Revisión exhaustiva del notebook adjunto

### E.1. Dictamen y alcance de la evidencia

**Dictamen:** el notebook tiene una base útil para construir y estudiar un dataset supervisado. Sus puntos fuertes son la unidad de 30 segundos, el cuidado de las etiquetas, la auditoría, las claves compuestas y la separación entre datos originales y representaciones candidatas. **Todavía no demuestra rendimiento de clasificación, beneficio de las reducciones ni ejecución integral coherente de todas las secciones sobre la cohorte amplia.** Antes de modelar, las prioridades son coherencia de ejecuciones, tiempo real, procedencia y escalas; no eliminar todos los extremos.

Se revisaron las **93 celdas**, el código de las **39 celdas no vacías de código**, las **163 salidas guardadas** y las **28 imágenes PNG**. No hay salidas de error guardadas. Se contrastaron código, tablas, gráficos, documentos y los dos CSV de epochs disponibles. Las celdas de código compilan sin errores de sintaxis; esto no equivale a ejecutar el notebook completo ni a probar su corrección científica.

| Evidencia | Alcance comprobable | Cómo usarla |
| :--- | :--- | :--- |
| EDA inicial | S002, S004 y S006; algunas inspecciones solo S002. | Ejemplos de estructura y comportamiento, no resultados de toda la cohorte. |
| Auditoría general guardada | 74 archivos completos, ninguno con error de lectura. | Incluye S097, aunque luego no entre al dataset supervisado. |
| ETL y análisis amplios guardados | 73 pacientes; 54.367 epochs; 128 columnas base. | Resultados descriptivos amplios de 3.1–3.7, salvo el análisis temporal nuevo. |
| Prueba temporal guardada, 3.4.3 | 18 pacientes; 13.165 epochs. | No presentar sus AUC ni cobertura como resultados de los 73 pacientes. |
| CSV base y candidato disponibles | 18 pacientes; 13.165 filas; 128 y 26 columnas. | Permitieron verificar claves y fórmulas en esta revisión, no reconstruir la cohorte amplia. |
| Vista cruda nueva, 3.3.2 | Código presente, sin salida guardada. | No afirmar que sus gráficos nuevos se observaron en el archivo adjunto. |
| Variantes, controles y exportación, 3.5.2–3.5.3 y 3.9.1–3.9.3 | Código presente, sin resultados guardados en esas celdas. | El diccionario de 3.9.4 sí tiene salida, pero no sustituye el registro de los controles anteriores. |
| Resumen breve nuevo de 3.6 | Código presente; la salida vieja sigue truncada. | Falta regenerarlo después de corregir sus cálculos temporales. |

**Límite de “cada salida”:** se leyó toda la información efectivamente almacenada. Cuando pandas guardó `...`, las filas ocultas no están en el notebook y no pueden recuperarse leyendo la imagen o el HTML. Esto afecta detalles de candidatos por paciente/tramo, la tabla AUC de 130 filas y el detalle antiguo de 3.6. Se revisaron sus filas visibles, el criterio generador y los gráficos asociados; no se inventaron valores de filas ausentes.

**Inconsistencias de procedencia que hay que cerrar:**

- `docs/guia-resumen-notebook.md` habla de 77 archivos, 76 pacientes y 56.850 epochs. Esas cifras **no coinciden con las salidas generales del adjunto revisado**, que muestran 74, 73 y 54.367. Pueden corresponder a otra versión; no mezclarlas en la exposición.
- El log guardado de 3.1 omite el encabezado de S095 y asocia aparentemente sus 580 epochs/una imputación con S091. La tabla de auditoría completa de 3.2 informa S091: **810 epochs, cero imputaciones**; S095: **580 epochs, una imputación**. Es una inconsistencia del registro guardado; no prueba que las filas del dataset estén asignadas al paciente equivocado. Regenerar el log y conciliarlo con la auditoría.
- Los avisos de 3.4 y 3.5.1 sobre salidas antiguas con `*_mean` quedaron desactualizados respecto de las tablas revisadas: estas ya muestran `HR_median`, `TEMP_median` y `EDA_median`. El problema actual es la mezcla de ejecuciones, no una media escondida en esas tablas.
- Los tipos del dataset calculado y los del CSV recargado pueden diferir (`float32` frente a `float64`; `object` frente a `str`). El CSV no conserva el esquema de pandas.

### E.2. Contexto, configuración y carga: secciones 0–1

**Lo correcto:** el objetivo es clasificación multiclase; la etiqueta no se trata como profundidad numérica. La sección 0.2 define claves por tipo de CSV y bloquea duplicados antes de escribir. `mode="w"` reemplaza, no acumula. Repetir `patient_id` no es duplicar una observación: S002 aporta **652 epochs diferentes** en los CSV comprobados.

**Qué falta:** registrar una identificación inequívoca del release, archivos, reglas y ejecución. Escribir DREAMT 2.2.0 en un título no demuestra que los CSV adjuntados sean de ese release. La fuente oficial informa correcciones de alineación en esa versión; contrastar origen y metadatos antes de atribuir toda inconsistencia al equipo. [Descripción y versiones de DREAMT](https://physionet.org/content/dreamt/2.2.0/).

**Dos precisiones sobre el dato:**

1. Las 100 filas por segundo corresponden al CSV sincronizado. Las frecuencias nativas informadas son BVP 64 Hz, ACC 32 Hz, EDA/TEMP 4 Hz y HR 1 Hz; el remuestreo no crea mediciones independientes. La PSG fue reducida a 100 Hz. Esto condiciona cambios entre muestras, señales planas y extracción de frecuencias. [DREAMT](https://physionet.org/content/dreamt/2.2.0/).
2. La cohorte original procede de un laboratorio de sueño; no asumir representatividad de población sana. Además, preparación (`P`) se codifica como W en archivos de 100 Hz: parte de la asociación movimiento–W podría describir preparación del registro. [DREAMT](https://physionet.org/content/dreamt/2.2.0/).

**Salida de carga:** S002 tiene 1.958.400 filas; S004, 2.413.100; S006, 2.403.000. Sus duraciones aproximadas son 5,44, 6,70 y 6,68 horas. El archivo original tiene 32 columnas; la muestra cargada tiene 33 al agregar `patient_id`. No hay una columna fuente extra ni un error por esa diferencia.

**Mejora práctica:** separar un modo exploratorio rápido de la reconstrucción amplia, sin reducir silenciosamente la cohorte. La lectura completa del primer paciente sirve para inspección, pero no debe considerarse una muestra aleatoria representativa.

### E.3. Estructura, etapas y señales: 2.1–2.2.2

Las tablas de estructura de los tres pacientes coinciden en nombres y tipos. Las etiquetas observadas son válidas. Eso permite integrar esquemas, pero no valida unidades, calidad o representatividad.

| Etapa | S002: muestras | S004: muestras | S006: muestras | Insight |
| :--- | ---: | ---: | ---: | :--- |
| W | 524.400 | 649.100 | 630.000 | Aproximadamente 26–27 % en cada registro; no equivale a calidad de sueño. |
| N1 | 192.000 | 489.000 | 369.000 | La proporción cambia entre pacientes. |
| N2 | 1.002.000 | 1.272.000 | 870.000 | Domina estos registros, pero no con la misma proporción. |
| N3 | 0 | 3.000 | 534.000 | S004 solo tiene un epoch N3: su caja no permite estudiar dispersión. |
| R | 240.000 | 0 | 0 | Ausencia observada en dos registros, no una clase “con valor cero”. |

**Las cuatro barras de 2.2.1** comparan cada registro y los tres juntos. La barra conjunta pondera más a los registros largos. Son frecuencias de muestras con etiquetas repetidas, no millones de anotaciones independientes. Las etapas ausentes no deben completarse inventando etiquetas.

**Las cinco figuras de 2.2.2 y la tabla de extremos:**

- `BVP_std`: en S002 la dispersión tiende a ser mayor en W/N1 que en N2/R. Puede describir onda, movimiento o contacto; no mide HRV.
- `E1_std` y `E2_std`: muestran diferencias por etapa, pero su patrón cambia entre pacientes. No basta la dispersión ocular para identificar REM de forma universal.
- `SNORE_std`: las escalas y distribuciones varían entre personas; una diferencia aislada no autoriza selección definitiva.
- `TEMP_mean`: las diferencias entre personas pueden superar las diferencias entre etapas. La temperatura de piel no es temperatura corporal central.
- Las cajas comparten escala dentro de cada figura y ocultan puntos extremos solo para dibujar. Esto facilita comparar, pero no prueba ausencia de extremos. La tabla conserva mínimos, máximos y recuentos.
- Redondear PSG a tres decimales produce ceros visuales: valores como `0,000012` aparecen como `0,000`. **No son señales constantes por ese motivo.** Usar notación científica o unidades verificadas.

**Conclusión:** el EDA inicial plantea buenas preguntas; sus pocos pacientes no alcanzan para generalizarlas. La evidencia amplia relevante aparece en 3.3–3.5.

### E.4. Faltantes y extremos individuales: 2.3–2.3.1

Las tablas no encuentran nulos, infinitos ni valores no numéricos en las 26 señales de S002/S004/S006. Correcto conservarlas sin imputar por esos motivos. **Un cero, una señal congelada o un valor rellenado previamente pueden ser finitos y pasar este control.**

En S002, los resúmenes crudos dan HR mediana cercana a 65,18 lpm; TEMP mediana 34,84 °C; EDA mediana 0,1396, media 0,2312 y máximo 1,6988; SAO2 mediana cercana a 0,9197. La separación entre media y mediana de EDA refleja asimetría, no necesariamente defecto.

La figura de extremos muestra, por separado, ventanas alrededor del mínimo y máximo de HR, TEMP, EDA y SAO2:

- HR cambia de manera más suave que una onda ECG: es una estimación ya procesada.
- TEMP presenta escalones pequeños; no interpretar cada repetición a 100 Hz como nueva medición.
- El entorno del mínimo EDA presenta un cambio de nivel; el máximo está rodeado de otras elevaciones. Mirar solo el punto extremo perdería ese contexto.
- SAO2 muestra escalones y exige comprobar escala/calidad antes de cualquier límite.

Los extremos pueden ocurrir en timestamps distintos y las escalas verticales son diferentes. No atribuir una causa común solo por aparecer en la misma figura. La sección es útil como inspección dirigida, no como regla universal de limpieza.

### E.5. Alineación, hipnograma y transiciones: 2.4–2.5

S002 tiene desplazamiento inicial de **2.400 muestras = 24 segundos**. Conserva 652 epochs completos: 1.956.000 muestras. Agrupar desde la primera fila mezclaría anotaciones; alinear antes de filtrar es una decisión central correcta.

La función comprueba timestamps finitos y diferencias de 0,01 segundos, e infiere la fase a partir de cambios entre etapas válidas. **Límite:** coincidencia de cambios con una grilla es evidencia interna, no verificación independiente con el archivo original de anotaciones PSG. Un registro sin suficientes cambios o con jitter requiere otra estrategia, no forzar una fase.

En S002 hay 652 epochs puros, sin empates ni etiquetas inválidas. La matriz contiene **651 pares consecutivos**, de los cuales **463 mantienen la etapa y 188 cambian**. La diagonal mide persistencia: no son 651 cambios de etapa.

El hipnograma muestra secuencia y tiempos; N2 aparece temprano y REM en tramos posteriores del registro mostrado. No prueba una regla para todos los pacientes. La posición vertical de R no representa mayor profundidad.

**Utilidad futura:** contexto de señales de epochs anteriores puede ayudar. No usar la etapa real anterior como entrada si no estará disponible al inferir; sería información privilegiada. No construir ventanas temporales a través de huecos.

### E.6. Auditoría amplia y alineación: 2.6–2.6.1

La salida registra 74 lecturas completas, cero errores, 72 alineaciones candidatas consistentes y dos inconsistentes. Los recuentos globales de nulos, infinitos y no numéricos en señales son cero. Los **609 casos de revisión no son 609 errores confirmados** ni 609 pacientes.

| Caso | Evidencia guardada | Interpretación / acción |
| :--- | :--- | :--- |
| S027 | Cambios con fases 1.900 y 2.900; `Missing` de filas 544.900–629.899, 85.000 muestras. | Tramo sin etiqueta de 850 s = 14 min 10 s y cambio de fase. No asumir EDA ausente. |
| S048 | Fases 0 y 2.900; no figura un tramo `Missing` en esa tabla. | La inconsistencia existe aun sin etiqueta explícitamente faltante. Revisar anotación/alineación. |
| S089 | Un tramo `Missing` de 3.000 muestras. | Una ventana de 30 s, candidata a imputación bajo la regla de vecinos. |
| S095 | Un tramo `Missing` de 3.000 muestras. | Mismo criterio; no interpolación libre. |
| S096 | Un tramo `Missing` de 3.000 muestras. | Mismo criterio; conservar marca de inferencia. |

**Cruce con los blancos de EDA:** S027 y S048 tienen EDA finita en todos los epochs retenidos. Las exclusiones por alineación son mucho mayores que el tramo `Missing` de S027: **113,48 minutos** de muestras fuera en S027 y **64,98 minutos** en S048. Por eso “blanco en el mapa”, “etiqueta Missing” y “EDA faltante” son conceptos distintos.

La regla de recuperación empieza en el primer cambio verificable y termina un epoch después del último cambio de cada fase. A partir de esa regla y las posiciones guardadas se deducen estos intervalos, que deben conciliarse con la auditoría de segmentos de la misma ejecución:

| Paciente | Segmentos deducidos, filas `[inicio, fin)` | Hueco interno deducido, minutos desde el CSV | Conciliación |
| :--- | :--- | :--- | :--- |
| S027 | `[1900, 79900)` y `[758900, 2276900)` | 13,32–126,48 | 26 + 506 = 532 epochs; 680.900 muestras fuera contando el inicio. |
| S048 | `[12000, 48000)` y `[374900, 2369900)` | 8,00–62,48 | 12 + 665 = 677 epochs; 389.900 fuera contando inicio y final. |

Estas deducciones no reemplazan inspeccionar las señales y anotaciones originales. Sí explican por qué la pérdida visual de EDA no requiere rellenar EDA: allí no hay epochs del ETL.

**Cómo dejar el cruce auditable:** tabla paciente × bloque de cinco minutos con epochs retenidos, cobertura temporal, intervalo recuperado y motivo de exclusión; consultar faltantes crudos de cada señal por separado. Un bloque parcialmente cubierto tampoco representa cinco minutos completos.

**Riesgo de implementación:** la recuperación especial está limitada a nombres S027/S048. Un nuevo paciente con dos fases puede detener 3.1. El antecedente de S077 con `[1400, 2400]` no queda resuelto por esta corrida: S077 no aparece entre los 74 archivos guardados. Recomendación: diagnóstico genérico y política explícita de rescate/revisión, no sumar excepciones sin auditar.

### E.7. SAO2: 2.6.2

La tabla marca **61 de 74 archivos** con alguna muestra fuera del rango exploratorio 0–1. Eso no significa que 61 registros completos estén mal. En varios, el porcentaje afectado es pequeño. La propia escala está pendiente de confirmación.

Las tres figuras aportan evidencia distinta:

- **S004:** caída brusca con sobrepaso alrededor del cambio; máximo aproximadamente 1,1249 y mínimo −0,1349.
- **S006:** cambio en sentido opuesto con sobrepasos semejantes; máximo aproximadamente 1,1249 y mínimo −0,1350.
- **S027:** prácticamente todo el registro cercano a 12, con variación mínima; todos sus valores quedan fuera de 0–1.

La simetría de sobrepasos alrededor de escalones sugiere revisar el remuestreo/filtrado de S004/S006. Es una **hipótesis**, no una causa confirmada. La serie de S027 no se arregla justificadamente dividiendo por 100: producir 0,12 no demuestra una medición válida.

**Decisión:** mantener SAO2 fuera del primer `X`, conservar origen y revisar metadatos, codificación y tramos. Si se recupera una señal fiable, podrían estudiarse nivel, percentiles o cambios de saturación; no calcular indicadores clínicos sobre una serie defectuosa. No borrar `Sleep_Stage` ni el paciente entero por un problema de esta señal.

### E.8. Señales constantes e IBI: 2.6.3

La tabla completa muestra IBI constante en S026, S030, S036 y S046, además de S097. S097 tiene **18 señales completamente constantes**; muchas PSG comparten exactamente `4,882887e-08`. Su wearable sí varía, y FLOW varía muy poco aunque no sea exactamente constante.

**S097:** la exclusión provisional del escenario PSG + wearable es defendible. No significa que todos sus sensores estén perdidos ni que se haya comprobado la causa. Para recuperarlo en wearable solo habría que confirmar primero que sus etiquetas PSG son confiables; hoy no hay evidencia suficiente para reintroducirlo.

La tabla de IBI también muestra tramos constantes enormes: S017 ≈98,33 % del registro, S058 ≈82,79 %, S055 ≈81,19 %, S044 ≈80,72 % y S067 ≈65,72 %. El IBI sincronizado no debe tomarse como una lista fiable de intervalos latido a latido para calcular HRV. Además, su unidad efectiva requiere comprobación.

Las tablas de tramos de al menos 30 s muestran:

- ACC_X/ACC_Y en 74 archivos y ACC_Z en 73: inmovilidad, cuantización o repetición pueden ser explicaciones válidas.
- BVP, EDA, TEMP y HR en 70 archivos: investigar si sus mesetas se superponen, especialmente cerca de bordes del registro. La coincidencia multisensor puede sugerir relleno o pérdida de adquisición, pero no se confirma solo con máximas duraciones separadas.
- Varios canales PSG con tramos constantes en **dos** pacientes: no atribuir todos a S097. Identificar el otro archivo y ubicar los intervalos.

**Mejora:** medir fracción plana, duración y coincidencia entre canales, usando tolerancias justificadas según precisión. “Exactamente constante” y “prácticamente constante” no son lo mismo. Los umbrales deben distinguir fallo de sensor de reposo real.

### E.9. EDA cruda: cada vista de 2.6.4

**Gráfico de máximos de los 74 archivos:** S057 ≈57,67; S004 ≈53,17; S027 ≈34,94; S043 ≈21,97; S082 ≈18,23. El eje está ordenado por máximo, **no por tiempo ni ID**. Una curva creciente en esa figura se produce por el ordenamiento; no es un patrón fisiológico. `log1p` se usa allí solo para visualizar. Rojo marca S004/S057 manualmente; azul no significa “calidad aprobada”.

**Tabla de estadísticos crudos:** S004 tiene mediana ≈0,324 y p99 ≈52,52; su media ≈10,64 y p75 ≈16,53 muestran que no es un único punto aislado. S057 tiene mediana ≈0,246 y p99 ≈32,73: nivel habitual bajo con episodios grandes. No plantear el mismo tratamiento para ambas trayectorias.

**Tabla de puntos máximos/mayores cambios y las figuras individuales:**

- S002: el mayor salto coincide con movimiento ACC y sucede **111,4 min después** del máximo EDA. El máximo no presenta ese mismo contexto de movimiento. No unir ambos como un solo evento.
- S004: el mayor salto sucede **35,7 min antes** del máximo. Coincide con movimiento/cambio de posición ACC; la elevación general de EDA continúa mucho después.
- S057: el mayor salto ocurre **11,4 min después** del máximo. El ACC cercano a ese salto es tranquilo; alrededor del máximo sí se ve movimiento previo. Por eso “no hubo movimiento” solo vale para la ventana concreta, no para todo el episodio. La subida rápida y el descenso prolongado merecen revisión, sin diagnóstico automático.

**Vista sincronizada de S004, minutos 190–230:** el ascenso visible de EDA comienza aproximadamente hacia el minuto 215. La línea del minuto **210 es una referencia dibujada**, no una detección. Hay movimiento previo, variación de HR y TEMP y varias etapas W/N1/N2. No aparece una correspondencia exclusiva con una etapa ni prueba causal. Conviene analizar inicio, duración y recuperación, no únicamente amplitud máxima.

**Acciones razonables:** conservar la marca; contrastar metadatos, contacto, saturación y señal nativa si existe; cuantificar duración por encima del propio nivel habitual y revisar conjuntamente movimiento y TEMP. Si se confirma defecto, invalidar/corregir solo la señal y tramo; si sigue incierto, conservar y hacer sensibilidad. Ni `log1p` ni mediana reparan un artefacto sostenido.

### E.10. Construcción del dataset: 3.1–3.2

La auditoría completa informa **74 archivos: 71 completos, 2 parciales y 1 excluido**. Resultado: **54.367 epochs × 128 columnas**, con aproximadamente 35,03 MB en memoria en la salida guardada y cero nulos. Los epochs conservados de S027/S048 son 532/677; S097 queda fuera.

**Qué representan las 128 columnas:** 24 señales × cinco resúmenes (`mean`, `std`, `median`, `n_valid`, `missing_frac`) = 120; más ocho columnas de identificación, tiempo, objetivo y calidad. No son 128 predictores aprobados. SAO2, IBI y las cuatro anotaciones de apnea no entran a esta tabla; las señales respiratorias medidas sí.

**Imputación de etiquetas:** tres epochs, uno en S089/S095/S096, equivalen a aproximadamente **0,0055 %** del total. El criterio exige un `Missing` completo aislado entre vecinos puros, físicamente contiguos e iguales dentro del fragmento. Se conserva pureza original e indicador de imputación. Es una decisión restringida y trazable; el epoch imputado no debe usarse como verdad independiente de prueba.

**La serie vacía de motivos de descarte** significa cero epochs rechazados entre las ventanas completas que llegaron a ese paso. No significa cero datos perdidos: las muestras descartadas por alineación, fragmentos incompletos y S097 ya quedaron fuera antes. La conciliación debe mostrar ambas vías.

**Lo bien hecho:** formación temporal antes de filtrar, resúmenes por señal, conservación del origen, pureza original, validación de claves, auditoría por archivo, caché y separación de incidencias/imputaciones.

**Lo que necesita mejora:**

1. `n_valid` se obtiene por recuento no nulo. No es necesariamente “muestras finitas y válidas instrumentalmente”: un infinito o un valor numérico de relleno puede contar. En esta cohorte auditada no hay infinitos crudos; el riesgo aparece al agregar otras fuentes o introducir invalidaciones.
2. Las funciones antiguas de limpieza de la celda anterior son no operativas y no participan del camino de 3.1. Su presencia puede confundir acerca de tratamientos aplicados. Documentar o retirar después ese código muerto, sin atribuirle transformaciones.
3. La recuperación de segmentos renumera epochs sucesivos, pero conserva el tiempo relativo real. Esto es válido como identidad; **no es válido usar luego `epoch × 30` como reloj**. E.16 reproduce el defecto.
4. El rescate es conservador y puede dejar fuera zonas estables anteriores/posteriores a cambios verificables. Es preferible perder una zona ambigua a inventar alineación, pero conviene cuantificar qué parte podría recuperarse con anotación independiente.
5. Si un archivo tardío falla, los resúmenes de pacientes anteriores todavía en memoria no garantizan una reconstrucción reanudable. Proponer checkpoint por paciente y escritura atómica; no un `except` que oculte la pérdida.
6. La caché compara rutas/tamaño/fecha y versiones de reglas. Es útil, pero requiere actualizar esa versión cuando cambia la lógica. Añadir huella de reglas/fuentes/salidas y fijar esquema al cargar mejora reproducibilidad.

**Doble lectura y costo:** en una ejecución sin caché, 2.6 recorre los CSV crudos y 3.1 vuelve a leerlos. Son dos pasadas completas con propósitos distintos, no duplicación de filas exportadas. La caché evita repetirlas en ejecuciones posteriores. Se puede estudiar una pasada conjunta de auditoría y agregación, o persistencia por paciente, sin cargar simultáneamente toda la señal cruda de la cohorte.

### E.11. Clases y distribuciones: 3.3–3.3.2

| Etapa | Epochs | Proporción | Pacientes con esa etapa | Lectura |
| :--- | ---: | ---: | ---: | :--- |
| W | 12.047 | 22,16 % | 73 | Movimiento/variabilidad pueden separar vigilia de sueño. |
| N1 | 6.389 | 11,75 % | 73 | Asociación univariada generalmente débil; no afirmar que será fácil. |
| N2 | 28.020 | 51,54 % | 73 | Mayoritaria; exactitud sola puede ocultar fallos en otras clases. |
| N3 | 2.059 | 3,79 % | 35 | Minoritaria en epochs y en pacientes. |
| R | 5.852 | 10,76 % | 61 | Menos frecuente que N2/W, pero no la clase más escasa. |

**Referencia aritmética, no modelo entrenado:** predecir siempre N2 acertaría 51,54 % sobre estos recuentos; su recuperación en las otras cuatro etapas sería cero. La exactitud equilibrada sería 20 % y F1 macro ≈0,136. Son cálculos de una regla trivial sobre la distribución completa, no métricas fuera de muestra.

**Las cajas de 3.3 y los seis pares histograma/caja de 3.3.2 muestran:**

- HR mediana: centro global ≈65,13 lpm; colas hasta 165,45; mucho solapamiento entre etapas. Un extremo no se convierte automáticamente en enfermedad o error.
- TEMP mediana: centro ≈34,33 °C; rango ≈20,31–37,57. Existe un grupo bajo cercano a 22 °C que amerita revisión de paciente/tramo/contacto, no un límite de temperatura central.
- EDA mediana: concentración cerca de valores bajos y cola hasta ≈57,27. La escala lineal comprime las cajas centrales; una vista logarítmica ayuda, sin borrar la cola.
- BVP_std: mediana ≈42,45 y máximo ≈550,32; W presenta mayor dispersión. No sustituye frecuencia cardíaca ni intervalos entre latidos.
- ACC_X_std: masa en cero/valores bajos y cola amplia; W destaca. El movimiento alto puede ser información de clase, aunque ciertos episodios sean artefactos.
- C4-M1_std: magnitudes del orden de `1e-5`; N3 se desplaza hacia mayor dispersión y R hacia menor. Es información real del resumen, no ruido causado por el número de decimales.

Las tablas de cobertura reportan 100 % para las características mostradas en cada etapa **dentro del dataset retenido**. En N3 participan 35 pacientes y en R 61: cobertura completa de valores no elimina el desbalance de sujetos.

**Vista cruda nueva:** está implementada para un paciente, con hasta 1.500 muestras por etapa para las cajas y cuantiles de todas sus muestras. No tiene salidas guardadas aquí. Comparará amplitud instantánea con los resúmenes, pero una caja cruda BVP no mide lo mismo que una caja de `BVP_std`. No usar esas miles de muestras como observaciones independientes para inferencias estadísticas.

### E.12. Todos los candidatos IQR: 3.3.1

Los 26 predictores revisados tienen 54.367 valores finitos. La tabla registra **marcas**, no pérdidas de calidad demostradas:

| Variable | Epochs marcados | % | Variable | Epochs marcados | % |
| :--- | ---: | ---: | :--- | ---: | ---: |
| EDA_std | 9.499 | 17,47 | Fp1-O2_std | 4.607 | 8,47 |
| ACC_X_std | 8.437 | 15,52 | C4-M1_std | 4.400 | 8,09 |
| SNORE_std | 8.223 | 15,12 | E2_std | 4.338 | 7,98 |
| EDA_median | 8.208 | 15,10 | F4-M1_std | 3.899 | 7,17 |
| RAT_std | 8.073 | 14,85 | ABDOMEN_std | 3.721 | 6,84 |
| ACC_Z_std | 7.959 | 14,64 | T3 - CZ_std | 3.514 | 6,46 |
| LAT_std | 6.698 | 12,32 | CZ - T4_std | 3.331 | 6,13 |
| ACC_Y_std | 6.409 | 11,79 | THORAX_std | 3.161 | 5,81 |
| O2-M1_std | 5.627 | 10,35 | BVP_std | 2.870 | 5,28 |
| E1_std | 5.109 | 9,40 | FLOW_std | 2.016 | 3,71 |
| PTAF_std | 5.066 | 9,32 | ECG_std | 1.820 | 3,35 |
| HR_std | 4.709 | 8,66 | HR_median | 1.619 | 2,98 |
| CHIN_std | 4.691 | 8,63 | TEMP_median | 1.484 | 2,73 |

No sumar estos porcentajes como epochs diferentes: un mismo epoch puede marcarse en varias variables. Tampoco eliminar cualquier fila con alguna marca sin calcular previamente la unión y el impacto por clase/paciente.

**Tabla por etapa:** ACC_X/Z/Y marcan aproximadamente 41,44/40,55/35,91 % de W. F4-M1 marca 28,65 % de N3; T3-CZ, 25,98 %; C4-M1, 24,77 %; CZ-T4, 24,19 %. Una limpieza global podría borrar justamente vigilia y la clase N3 minoritaria que se busca reconocer.

**Tablas por paciente y tramo:** ABDOMEN_std marca 679/687 epochs de S084 y 710/767 de S086. TEMP concentra marcas en S021 y S016; sus tramos destacados duran aproximadamente 162 y 105,5 minutos. Eso orienta a diferencias sostenidas de escala/nivel o adquisición, no a unos pocos puntos aislados. Inspeccionar antes de aplicar una regla común.

**Tabla de casos extremos:** EDA_std de S057 epoch 330 alcanza ≈16,267 frente a un límite superior IQR ≈0,01161. S004 epoch 797 llega a ≈5,138. Son prioridades de inspección temporal. La distancia de miles de IQR se explica en parte por un IQR central diminuto; no compara gravedad clínica entre señales. Límites negativos de una desviación estándar son resultados del criterio estadístico, no valores físicamente permitidos.

**Problema compartido con 3.6:** los vecinos y tramos consecutivos se definen con diferencias de `epoch`. Deben exigir también 30 segundos reales entre inicios y no cruzar segmentos. Un tramo marcado separado por un hueco no es actividad continua.

**Decisión:** no hay justificación para clipping o eliminación global por IQR. Agregar contexto, unidades y análisis de sensibilidad dirigido. El detalle guardado está truncado y requiere regeneración si se quiere discutir cada caso individual.

### E.13. EDA de todos los incluidos: 3.3.3

La tabla completa comprende **73 pacientes**, cada uno con cobertura EDA de 100 % en sus epochs retenidos. La mediana por paciente va aproximadamente de **0,004 en S046 a 5,476 en S098**. Esta heterogeneidad explica por qué comparar valores absolutos sin contexto puede confundir identidad/nivel basal con etapa.

| Paciente | Mediana por epoch | p95 | p99 | Máximo de mediana de epoch | Qué sugiere |
| :--- | ---: | ---: | ---: | ---: | :--- |
| S004 | 0,322 | 45,269 | 52,489 | 52,871 | Elevación importante durante parte del registro, no solo un pico crudo. |
| S057 | 0,244 | 6,069 | 31,401 | 57,268 | Episodio grande con nivel central bastante menor. |
| S027 | 5,225 | 13,170 | 30,502 | 34,773 | Nivel habitual alto y cola; registro parcialmente retenido. |
| S048 | 0,659 | 2,772 | — | 3,543 | Blanco temporal no equivale a EDA inválida en los epochs conservados. |
| S098 | 5,476 | 6,132 | — | 6,251 | Nivel habitualmente alto y menos variable; tratamiento distinto de S057. |

El guion `—` indica que aquí no se reproduce ese percentil, no un faltante del dataset. S028, S022, S045, S031, S043 y S025 también tienen medianas relativamente altas. La lista de revisión manual S004/S057 no agota todos los casos que podrían merecer revisión.

**Gráfico mediana/p95:** permite distinguir nivel habitual de episodios altos. No indica causa ni calidad. **Mapa de cinco minutos:** muestra la mediana de los resúmenes por epoch; no un máximo crudo ni todos los detalles de la señal. Puede ocultar un episodio breve o dar igual apariencia a bloques con distinta cobertura. Añadir número de epochs por bloque si se usa para comparar pacientes.

**Para el modelo:** conservar inicialmente nivel y variabilidad de EDA como familias distintas. Su asociación simple con etapa es modesta; medir el aporte incremental y la estabilidad por persona. `log1p` comprime la escala pero no elimina las diferencias basales. Una normalización personalizada debe definir qué información del nuevo paciente estará disponible: usar toda su noche futura no es válido para un escenario en tiempo real.

### E.14. Correlaciones y AUC por etapa: 3.4–3.4.2

**Primer mapa, wearable:** EDA mediana/EDA_std ≈0,60; pares ACC ≈0,54–0,58. Hay información compartida, no equivalencia exacta. BVP_std/HR mediana ≈0,03: HR se obtiene de BVP, pero dispersión de amplitud y frecuencia de pulso son propiedades diferentes. La procedencia de una señal no obliga a que todos sus resúmenes estén correlacionados.

**Segundo mapa, wearable–PSG:** los valores mostrados son generalmente modestos, aproximadamente −0,18 a 0,30. No demuestra que un wearable reemplace una PSG ni que no pueda ayudar junto con ella.

**Tabla completa de seis pares por encima de 0,85:**

| Par | Spearman | Acción justificada |
| :--- | ---: | :--- |
| C4-M1_std / F4-M1_std | 0,934897 | Ablación alternativa de cada canal; no quitar ambos ni uno automáticamente. |
| T3 - CZ_std / CZ - T4_std | 0,923503 | Comparar cada retiro sobre la misma referencia. |
| E1_std / E2_std | 0,894712 | Comparar dos canales frente a resumen, calidad y asimetría. |
| C4-M1_std / T3 - CZ_std | 0,872791 | Revisar redundancia dentro de pacientes y aporte conjunto. |
| C4-M1_std / CZ - T4_std | 0,869670 | Mismo criterio, con atención a N3/R. |
| C4-M1_std / O2-M1_std | 0,868792 | Comparación específica, no eliminación por umbral. |

Spearman no permite decir que una columna “explica” causalmente a otra. La correlación agrupada puede incluir diferencias entre pacientes y diferencias entre etapas. Priorizar correlación **dentro de paciente**, distribución de coeficientes y estabilidad por etapa antes de discutir redundancia. Para evaluar utilidad final, usar ablación fuera de paciente, no una correlación residual con toda la cohorte.

**Tercer mapa, etapa contra el resto:** muestra `d = 2 × AUC − 1`, no AUC directa ni exactitud. `d=0,78` corresponde a AUC 0,89. La AUC de rangos compara si un valor de la etapa tiende a superar uno del resto; empates aportan medio. No entrenó un clasificador. [Referencia de ROC AUC](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html).

| Familia / etapa | Evidencia del mapa | Insight |
| :--- | :--- | :--- |
| EEG / N3 | d ≈0,775 C4; 0,793 F4; 0,796 T3-CZ; 0,785 CZ-T4; 0,724 Fp1-O2; 0,597 O2. | Es la separación univariada más fuerte. Mantener EEG en la referencia PSG. |
| EEG / R | d negativo, aproximadamente −0,43 a −0,56 en varios canales. | R tiende a menor dispersión. Un AUC <0,5 puede ser útil en dirección inversa; no es fracaso del predictor. |
| ACC / W | d ≈0,42–0,44. | La actividad motora es una candidata fuerte para separar vigilia. |
| CHIN, LAT, RAT / W | d ≈0,44; 0,37; 0,34. | Actividad muscular añade una pregunta de aporte adicional a ACC. |
| HR_std / N3 y N2 | d ≈−0,405 y −0,31. | Menor variación HR en estas comparaciones; no equivale a HRV. |
| BVP_std / W | d ≈0,293. | Señal moderada, consistente con el análisis por paciente. |
| EDA_std / W | d ≈0,220. | Variabilidad tiene una asociación distinta del nivel mediano EDA. |
| E1/E2_std | d N3 ≈0,475/0,588; R cerca de cero o ligeramente negativo. | El resumen std ocular no está capturando un marcador REM fuerte en esta muestra. No generalizar esto a toda la señal EOG. |
| TEMP, SNORE, ECG y respiratorias | Asociación simple más débil; SNORE máxima d ≈0,036. | Familias secundarias para ablación y revisión de escalas; no necesariamente inútiles en combinación. |
| N1 | Separación univariada generalmente pequeña. | Hipótesis de mayor dificultad; todavía no hay errores de modelo medidos. |

Para EOG, la asociación con N3 podría involucrar información compartida con EEG, adquisición o composición de pacientes; son explicaciones a investigar. Se necesita morfología/frecuencia/calidad, no atribuir la causa a partir del mapa.

Una AUC cercana a 0,5 solo indica poca separación con ese ordenamiento escalar: puede haber relaciones no monótonas, ciclos o interacciones. Ningún valor aquí demuestra generalización en personas nuevas.

### E.15. Prueba temporal y sus tres figuras: 3.4.3

La salida temporal analiza **13.165 epochs de 18 pacientes**, con cero tiempos/etapas inválidos. Su desbalance difiere del amplio: W 4.267; N1 1.589; N2 5.744; N3 438; R 1.127. No mezclar ambos denominadores.

| Etapa | Mediana del tiempo desde el CSV, min | AUC global | Mediana AUC dentro de paciente | Pacientes evaluables |
| :--- | ---: | ---: | ---: | ---: |
| W | 205,617 | 0,567 | 0,633 | 18 |
| N1 | 175,183 | 0,471 | 0,458 | 18 |
| N2 | 163,500 | 0,436 | 0,406 | 18 |
| N3 | 92,750 | 0,310 | 0,260 | 5 |
| R | 247,000 | 0,633 | 0,673 | 14 |

**Figura de tiempos por etapa:** N3 aparece relativamente antes y R después en esta ejecución. Tiempo cero es el inicio del CSV, no necesariamente comienzo de la noche o primer sueño. N2 puede aparecer temprano sin contradicción: el registro no obliga a comenzar en W/N1.

**Mapa paciente × etapa:** AUC >0,5 indica tendencia a tiempos mayores; <0,5, menores. Gris significa comparación no evaluable, no AUC cero. Ejemplos: R S017 ≈0,973 y S010 ≈0,884, pero S009 ≈0,388 y S088 ≈0,333. **No todos presentan REM más tarde.** S087 tiene W ≈0,984 y N2 ≈0,037: un patrón extremo que conviene revisar en su secuencia, no eliminar por ser diferente.

N3 aparece en siete pacientes de esa muestra, pero solo cinco reúnen al menos cinco epochs en ambos grupos. El 71,43 % de los 14 evaluables para R supera 0,5; no es una probabilidad de que un individuo esté en REM.

**Figura de proporción, promedio y cobertura:**

- Arriba: cuenta todos los epochs de un bloque y calcula el porcentaje por etapa. Quien aporta más epochs válidos tiene más peso.
- Medio: calcula porcentajes por paciente observado en el bloque y promedia con igual peso. Un paciente con pocos epochs puede pesar lo mismo que otro con el bloque completo.
- Abajo: pacientes con al menos un epoch en ese bloque; no total de epochs ni pacientes por etapa. Las marcas enteras y el conteo sobre las barras son apropiados.
- El eje X corresponde a bloques de 30 minutos desde el inicio del CSV. Los puntos representan bloques, no una etapa instantánea ni una alineación por comienzo fisiológico del sueño.
- La cobertura es 18 hasta el bloque 240–270 min; luego 17, 17, 15, 12 y **4** en 390–420. Interpretar el final con mucha cautela: cambia la composición y quedan bloques parciales.

Los 15 controles guardados prueban coherencia de cálculo, no significación estadística ni poder predictivo. Hay asociación temporal descriptiva, especialmente N3/R, pero no un orden determinista. No hacer pruebas tratando 13.165 epochs autocorrelacionados como sujetos independientes.

**Pendiente:** repetir sobre la cohorte amplia y comparar A: señales; B: solo tiempo real; C: señales + tiempo, con las mismas particiones. No normalizar por duración final si esa duración es desconocida al inferir. No agregar `epoch` y tiempo relativo como dos relojes redundantes por defecto.

### E.16. Ficha, consistencia y variantes: 3.5–3.5.3

La ficha tiene **72 características**: 24 señales × media/desviación/mediana, con cobertura 100 % en 73 pacientes. Los controles de cobertura no están en esas 72 filas. Tener muchos valores distintos ayuda a descartar constancia literal, pero no garantiza información útil. `None/NaN` en asociación de una media significa **no incluida en el análisis de las 26 características**, no falta de datos ni asociación nula.

La tabla de 40 contrastes exige cinco epochs en cada grupo. Resume medianas por paciente y proporción de diferencias positivas, no una prueba de hipótesis. Todos los contrastes W/N1/N2 usan 73 evaluables; N3, 26; R, 61.

| Variable | W: diferencia / % positiva | N1 | N2 | N3 | R |
| :--- | :--- | :--- | :--- | :--- | :--- |
| HR_median | +2,43 / 84,93 % | −0,22 / 46,58 % | −1,42 / 21,92 % | +2,46 / 61,54 % | +0,04 / 50,82 % |
| TEMP_median | −0,08 / 42,47 % | −0,06 / 36,99 % | −0,02 / 43,84 % | +0,22 / 73,08 % | +0,01 / 50,82 % |
| EDA_median | −0,01 / 43,84 % | ≈0 / 43,84 % | ≈0 / 47,95 % | ≈0 / 50,00 % | +0,01 / 55,74 % |
| BVP_std | +12,86 / 86,30 % | −1,39 / 36,99 % | −2,86 / 28,77 % | +0,76 / 53,85 % | −1,56 / 39,34 % |
| ACC_X_std | +0,30 / 97,26 % | +0,02 / 57,53 % | −0,11 / 10,96 % | −0,07 / 38,46 % | −0,03 / 40,98 % |
| C4-M1_std | magnitud pequeña / 50,68 % | pequeña / 10,96 % | pequeña / 80,82 % | pequeña / **100 %** | pequeña / **3,28 %** |
| E1_std | magnitud pequeña / 82,19 % | pequeña / 30,14 % | pequeña / 30,14 % | pequeña / 92,31 % | pequeña / 45,90 % |
| FLOW_std | magnitud redondeada / 78,08 % | redondeada / 54,79 % | redondeada / 28,77 % | redondeada / 38,46 % | redondeada / 42,62 % |

Las diferencias pequeñas/redondeadas no se interpretan como cero exacto; pedir salida científica para cuantificar su magnitud. Las unidades entre filas no son comparables. El complemento de “positiva” incluye diferencias cero: no llamar a todos los restantes “negativos”.

**Insights fuertes:** ACC_X mayor en W en 71/73 pacientes; BVP_std mayor en W en 63/73; C4-M1_std mayor en N3 en 26/26 evaluables y positiva en R solo en 2/61. La evidencia favorece preservar estas familias en la referencia. EDA mediana presenta dirección mucho menos consistente. HR no disminuye ordenadamente de W a N3 en esta tabla: N3 es mayor que el resto en parte de los pacientes, posiblemente por composición temporal/etapas; no imponer una interpretación clínica simplista.

**3.5.2–3.5.3:** define 14 variantes y verifica construcción, índice y finitud. En esta revisión se ejecutaron esas dos celdas en memoria sobre el CSV disponible de 18 pacientes, sin escribir resultados ni entrenar: **las 14 son construibles y conservan los 13.165 epochs**. No se agregaron tests externos ni se alteró el notebook. La salida actual aún necesita registrarse dentro del notebook para la cohorte que se exponga.

- PSG + wearable: referencia 26 predictores; ojos o piernas 25; ACC 24; cada ablación EEG 25; candidata combinada 22.
- Wearable solo: referencia nueve; norma ACC y candidata combinada siete.
- La variante `log1p_colas` conserva nombres y cantidad de columnas aunque cambie valores. Una tabla de columnas agregadas/retiradas no describe por sí sola ese cambio: registrar fórmula y versión también.

**Defecto temporal confirmado en 3.6:** se ejecutó en memoria el código existente con tres epochs sintéticos, IDs 0/1/2, inicios 0/30/3.600 s y etapas N2/N2/R. No se creó un archivo de test ni se modificó el notebook.

| Indicador | Código actual | Resultado usando tiempo real |
| :--- | ---: | ---: |
| Duración válida | 1,5 min | 1,5 min |
| Tramo entre inicio y final observado | **1,5 min** | **60,5 min** |
| Huecos | **0** | **1** |
| Cambios entre epochs físicamente contiguos | **1** | **0** |
| Latencia REM desde primer sueño observado | **1 min** | **60 min** |

**Causa:** 3.1 renumera los segmentos recuperados sin dejar saltos en `epoch`; 3.6 usa ese ordinal como tiempo. **Corrección propuesta:** ordenar por `tiempo_relativo_segundos`, exigir diferencia de 30 s con tolerancia para continuidad, calcular latencia por resta de timestamps relativos y tramo por último inicio +30 s menos primer inicio. Aplicar el mismo criterio a vecinos/tramos de 3.3.1. Conservar `epoch` como clave, no convertirlo en reloj. Este defecto está identificado, **no corregido en el notebook durante esta revisión**.

### E.17. Las tres distribuciones entre pacientes: 3.6

La salida guardada resume 73 pacientes: **38 sin N3 observado y 12 sin R observado**. El código actual agrega tabla de cuantiles y evita truncar filas, pero esas mejoras todavía no aparecen en la salida antigua.

**Primer gráfico, boxplot:** cada observación subyacente es el porcentaje de una etapa de **un paciente**, no el valor de una señal ni un epoch. Para cada etapa hay 73 porcentajes; la línea central es su mediana entre personas y la caja reúne el 50 % central. N2 suele ocupar la mayor proporción; W varía mucho; N3 tiene mediana cero porque más de la mitad de los pacientes no la presentan en los epochs retenidos. Esto **no muestra cómo pasan por etapas a lo largo del tiempo**.

**Segundo gráfico:** histograma de minutos válidos retenidos por persona; muchos registros se concentran visualmente alrededor de 350–400 min. No representa necesariamente toda la noche ni horas fisiológicas de sueño: incluye W y excluye zonas no retenidas.

**Tercer gráfico:** distribución de latencia REM para los 61 pacientes con R observado. Los otros 12 no tienen latencia cero; su valor no está observado. Además de este sesgo de selección, la latencia actual puede estar subestimada en pacientes parciales por el defecto anterior. No interpretar clínicamente ni comparar secuencias hasta corregirlo.

**Lo aprovechable ahora:** porcentajes, conteos, etapas no observadas y duración válida. **Recalcular:** latencia, tramo total, huecos y transiciones en pacientes con segmentos. Los indicadores derivados de `Sleep_Stage` sirven para auditoría/evaluación de noches; incluirlos en `X` sería fuga del objetivo.

### E.18. Controles lógicos y ceros: 3.7

La salida informa sin violaciones de reglas de recuentos/fracciones/std; las tablas de casos y desglose por etapa están vacías. Es evidencia positiva de coherencia lógica, no certificación instrumental.

| Variable descrita | Resultado | Pregunta útil |
| :--- | :--- | :--- |
| HR_mean | Finita en 54.367 epochs; rango ≈39,135–164,963; sin ceros. | Revisar extremos en contexto; no establecer límites clínicos por esta tabla. |
| TEMP_mean | Rango ≈20,129–37,574; sin ceros. | Inspeccionar pacientes/tramos bajos y contacto. |
| EDA_mean | 135 epochs cero en cinco pacientes. | Determinar reposo de señal, codificación o meseta; no imputar cero automáticamente. |
| BVP_std | **71 epochs cero en 68 pacientes**. | Patrón casi de una ventana por persona: buscar bordes o relleno multisensor. Es hipótesis, no fallo confirmado. |
| ACC_X_std | 4.718 epochs cero en los 73 pacientes, ≈8,68 %. | Compatible con inmovilidad/cuantización; contrastar sin borrar sistemáticamente. |
| C4-M1_std | Un epoch cero en un paciente. | Identificarlo y revisar señal cruda/calidad. Otros ceros impresos pueden ser redondeo. |

IBI y SAO2 no se describen aquí porque no están en el ETL actual. Agregar controles explícitos de finitud para todos los predictores y de pureza original/etiqueta imputada. Mostrar tamaño y cohorte junto a cada control para no trasladar un “OK” de 18 pacientes a 73.

### E.19. Transformación y diccionario: 3.8–3.9.4

3.8 distingue ETL de modelado y rechaza la poda por correlación. Es una orientación adecuada, pero debe actualizarse junto con salidas coherentes y los defectos aquí identificados. No afirmar que toda limpieza está cerrada por no encontrar nulos.

3.9 materializa una candidata de **26 columnas totales: 22 predictores, tres metadatos de trazabilidad y un objetivo**. La referencia original combinada tiene 26 **predictores**: son dos cifras iguales con significado distinto.

En los CSV disponibles, base y candidato tienen 13.165 filas, 18 pacientes, cero claves repetidas y cero instantes repetidos por paciente. Sus claves, tiempos y etiquetas son idénticos. Se reconstruyó en memoria la candidata con la función existente: **sus 22 columnas concuerdan numéricamente con el CSV candidato**. Esto comprueba la transformación de esos archivos, no beneficio predictivo ni exportación amplia de 73 pacientes.

| Transformación escrita | Tipo | Qué conserva / pierde |
| :--- | :--- | :--- |
| Muestras → epochs de 30 s | Agregación temporal | Conserva resumen/etiqueta; pierde forma detallada de onda. |
| Media, mediana y std | Extracción de características | Describe nivel y dispersión; no recupera frecuencia ni orden de las muestras. |
| E1/E2 → EOG_max_std | Reducción bilateral candidata | Conserva mayor dispersión; pierde lateralidad y comportamiento del otro canal. |
| LAT/RAT → LEG_max_std | Reducción bilateral candidata | Conserva actividad máxima; pierde asimetría y puede priorizar el canal ruidoso. |
| Tres ACC_std → norma | Reducción multieje candidata | Resume dispersión total; pierde información por eje. |
| BVP_std, EDA_median y norma ACC → log1p | Cambio de escala no lineal | Comprime colas, conserva orden/ceros; no recorta ni repara. |
| Selección de columnas para `X` | Selección provisional | Metadatos y alternativas salen de la entrada del algoritmo, no del ETL original. |
| Missing aislado → etiqueta inferida | Imputación restringida del objetivo | Tres casos amplios; no se imputaron señales ni tramos largos. |

**No aplicado:** escalado aprendido, binning de predictores, clipping, balanceo de clases, reducción EEG definitiva ni entrenamiento. Los bloques de cinco/30 minutos son agrupaciones para gráficos, no binning usado como predictor.

Los doce controles de 3.9.2 y nueve de identidad de 3.9.3 están escritos y condicionan la exportación. Sus salidas no están guardadas en esas celdas del adjunto; la verificación anterior del apartado D es un antecedente de 18 pacientes, no evidencia amplia nueva. La tabla de 3.9.4 tiene 26 filas y describe tipos/roles correctamente, sin convertir columnas.

**Riesgo de trazabilidad:** el candidato conserva ID/epoch/tiempo/etapa, pero no guarda `etiqueta_imputada`, pureza o cobertura. Están en el ETL base; para excluir etiquetas inferidas de evaluación hay que unir por clave y versión, o conservarlas como **metadatos fuera de `X`** en una exportación posterior. “Fuera de X” no debería obligar a perderlas del archivo de trabajo.

### E.20. Secciones 4–7 y documentación

La sección 4 propone algoritmos y evaluaciones, sin ejecutarlos. 5–7 son espacios reservados; no hay matrices de confusión, clasificación reportada ni importancia de variables aprendida. La asociación descriptiva no llena esos espacios como si fueran resultados predictivos.

El plan canónico es `plan-ejecucion-transformacion.md`; `plan-transformacion-etl.md` es un enlace de compatibilidad, no un segundo plan. Hay cifras y estados históricos en la guía y ADR: conservar historia, pero distinguirla del estado actual. No convertir decisiones metodológicas propias en exigencias de la cátedra sin la consigna correspondiente. El material de entrega anterior también documenta corridas menores; sus números no reemplazan los del adjunto actual.

## F. Decisión razonada sobre todas las familias de columnas

### F.1. Qué conservar, qué dejar fuera y qué comparar

**`X` significa la tabla de entradas que recibirá un algoritmo; `y` es `Sleep_Stage`.** El CSV puede guardar ambas y metadatos que el algoritmo no ve. La selección inicial busca una referencia interpretable, no declarar inútil todo lo restante.

| Grupo | Recomendación inicial | Motivo y condición de revisión |
| :--- | :--- | :--- |
| `patient_id` | Conservar como metadato; fuera de X. | Separar personas entre particiones y auditar; no usar identidad numérica como fisiología. |
| `epoch` | Conservar como clave/orden; fuera de X inicial. | No mide correctamente tiempo real a través de segmentos. |
| `tiempo_relativo_segundos` | Conservar; predictor solo en comparación temporal. | Asociación descriptiva existente; aporte futuro por medir. |
| `TIMESTAMP` | Auditoría, fuera de X. | Está desplazado; no es un reloj fisiológico comparable entre pacientes. |
| `Sleep_Stage` | Objetivo, nunca predictor. | Evita fuga directa. |
| Pureza original/final e imputación de etiqueta | Conservar para calidad; fuera de X. | Derivadas de anotaciones; necesarias para excluir inferencias de evaluación. |
| `*_n_valid`, `*_missing_frac` | Metadatos iniciales. | Son redundantes entre sí con ventana fija; cobertura no equivale a calidad. Si son constantes no ayudan como predictores. |
| HR mediana y std | Conservar en referencia. | Nivel y variación son diferentes; W muestra patrón consistente. Comparar media después. |
| TEMP mediana | Conservar provisionalmente. | Asociación débil pero potencial conjunta; revisar niveles bajos/entre pacientes. |
| EDA mediana y std | Conservar para comparación; revisar calidad. | Nivel basal y cambios son distintos; probar log del nivel sin borrar episodios. |
| BVP_std | Conservar. | Evidencia W consistente; no interpretarlo como HRV. Medias/medianas BVP como alternativas, no prioritarias. |
| ACC_X/Y/Z_std | Conservar la referencia de tres ejes. | Correlación moderada y señal W fuerte; norma es una alternativa, no sustitución aprobada. |
| Medias/medianas ACC | Comparar después como postura/orientación. | No se demostraron inútiles; disponibilidad/calibración y rotación condicionan generalización. |
| Seis EEG_std | Conservar en referencia PSG. | Fuerte separación N3 y patrón opuesto en R; ablaciones necesarias. |
| E1/E2_std | Conservar separados en referencia. | Resumen bilateral puede perder información; explorar características que capturen dinámica ocular. |
| CHIN_std y LAT/RAT_std | Conservar inicialmente. | Asociación con W y posible complementariedad. Máximo de piernas queda candidato. |
| ECG_std | Familia secundaria para ablación. | La amplitud ECG no resume ritmo; no eliminar por asociación simple baja. |
| SNORE_std | Prioridad menor para aporte incremental. | Separación univariada muy débil y heterogeneidad de escala. |
| PTAF/FLOW/THORAX/ABDOMEN_std | Provisionales con revisión de escalas. | El resumen respiratorio puede aportar, pero FLOW y otras amplitudes cambian mucho entre personas. |
| Medias/medianas de PSG oscilatoria | Fuera de primera referencia, no borradas. | Pueden describir offset/cambio de sensor; evaluar si hay significado y aporte, no seleccionar por media cercana a cero. |
| SAO2 e IBI | Fuera del primer modelo hasta verificar. | Calidad/escala no resuelta; mantener fuente. |
| Apneas anotadas y resúmenes derivados de etapas | Fuera del modelo principal. | Anotaciones/contexto privilegiado o fuga del objetivo; no confundir con señales respiratorias. |

### F.2. Hallazgo adicional de escalas: FLOW y otras amplitudes

La revisión del CSV disponible de **18 pacientes** muestra dos grupos de magnitud muy distintos en FLOW_std: medianas próximas a `0,00004–0,00023` en algunos pacientes y `0,10–0,22` en otros. Ejemplos comprobados:

| Paciente | Mediana FLOW_std | Máximo FLOW_std |
| :--- | ---: | ---: |
| S002 | 0,000044 | 0,000482 |
| S004 | 0,000093 | 0,000642 |
| S005 | 0,127145 | 0,343525 |
| S006 | 0,101101 | 0,285692 |
| S083 | 0,215000 | 0,438627 |
| S088 | 0,000038 | 0,000456 |

Entre las medianas de S083/S088 hay un factor aproximado de **5.667**. Es un hallazgo de heterogeneidad, **no confirmación de conversión incorrecta**. En la tabla amplia, FLOW_std tiene mediana ≈0,000202 y p99 ≈0,3418, consistente con la necesidad de estudiar esa mezcla.

En los mismos 18 pacientes, las razones máximo/mínimo positivo de medianas son aproximadamente 555 para ABDOMEN_std, 269 para RAT_std, 243 para SNORE_std y 189 para PTAF_std. Pueden incluir biología, tiempo despierto, ganancia de sensor o procesamiento. No extrapolar estos cocientes a los 73 sin recalcular.

**Acción prioritaria:** tabla por paciente con unidades/procedencia, nivel, dispersión, histogramas y calidad. Si se confirma un factor de conversión, corregirlo desde la fuente y recalcular; si son amplitudes de sensores distintos, explicitarlo y comparar representaciones robustas/personalizadas compatibles con inferencia. No “resolver” una unidad equivocada con escalado o log: ambos pueden ocultarla sin corregirla.

### F.3. Columnas de la copia candidata efectivamente comprobada

La tabla siguiente cubre sus 26 columnas. El tipo general de decimales es `float`; la lectura actual de CSV usa `float64`. Los dos identificadores son `int64`; la etapa es texto/categoría (`object` o `str` según pandas).

| Columna(s) | Tipo | Rol / interpretación | Decisión |
| :--- | :--- | :--- | :--- |
| `patient_id` | int | Persona; agrupación y trazabilidad. | Fuera de X. |
| `epoch` | int | Identificador secuencial de ventana. | Fuera de X; no reloj físico. |
| `tiempo_relativo_segundos` | float | Inicio real relativo de la ventana. | Metadato en esta candidata. |
| `Sleep_Stage` | object | Etapa a predecir. | y. |
| `HR_median` | float | Nivel de frecuencia cardíaca del epoch. | Conservar referencia. |
| `HR_std` | float | Variación de HR dentro de 30 s, no HRV. | Conservar referencia. |
| `TEMP_median` | float | Nivel de temperatura de piel. | Provisional, revisar bajos. |
| `EDA_std` | float | Variación de conductancia dentro de 30 s. | Provisional, calidad/colas. |
| `C4-M1_std`, `F4-M1_std`, `O2-M1_std`, `Fp1-O2_std`, `T3 - CZ_std`, `CZ - T4_std` | float, seis | Dispersión de seis canales EEG. | Conservar; comparar ablaciones. |
| `CHIN_std` | float | Dispersión muscular del mentón. | Conservar referencia. |
| `ECG_std` | float | Dispersión de amplitud ECG. | Evaluar aporte, no confundir con ritmo. |
| `SNORE_std` | float | Variación del canal de ronquido. | Prioridad secundaria. |
| `PTAF_std`, `FLOW_std`, `THORAX_std`, `ABDOMEN_std` | float, cuatro | Dispersión de canales respiratorios. | Revisar escalas antes de concluir. |
| `EOG_max_std` | float | Mayor std entre E1/E2. | Reducción no validada. |
| `LEG_max_std` | float | Mayor std entre LAT/RAT. | Reducción no validada. |
| `BVP_std_log1p` | float | Log de la dispersión óptica. | Transformación candidata. |
| `EDA_median_log1p` | float | Log del nivel central EDA. | Transformación candidata. |
| `ACC_axes_std_norm_log1p` | float | Log de norma de las tres std ACC. | Reducción + escala candidatas. |

**Sustituidas solo en esta candidata:** E1/E2, LAT/RAT y los tres ACC_std por resúmenes; BVP_std y EDA_median por log. **No eliminadas del ETL:** esas nueve columnas, las alternativas de media/mediana y metadatos de calidad. **No eliminados por correlación:** los seis canales EEG_std. Antes de entrenar, elegir explícitamente una lista de predictores; no pasar el CSV entero al algoritmo.

## G. Transformaciones: qué mejoran, qué no y dónde aplicarlas

### G.1. Mediana, desviación y señal cruda

La mediana y la desviación estándar **se calculan a partir de valores reales**, no los reemplazan por valores inventados. Responden preguntas distintas:

- Mediana: nivel típico de la señal dentro del epoch; menos afectada por pocos picos.
- Media: promedio; sensible a picos y útil cuando ese nivel tiene significado.
- Std: dispersión de las muestras respecto de su media; útil para amplitud/actividad de ondas que promedian cerca de cero.
- Varianza: std al cuadrado; misma información con unidades al cuadrado. No aporta una propiedad independiente si se agrega junto con std.
- Señal cruda: conserva forma, orden y frecuencias; requiere extracción adicional o modelos de secuencia. Dos ondas con la misma mediana/std pueden tener frecuencias completamente distintas.

**Ventaja actual:** tabla compacta, interpretable y fácil de comparar. **Costo:** los tres resúmenes no conservan husos, formas de ondas, direcciones, periodicidad o todos los picos. Es una línea base legítima; no equivale a capturar toda la fisiología disponible. BVP_std no es HRV, HR_std tampoco es variabilidad de intervalos y ECG_std no es frecuencia cardíaca.

### G.2. log1p y escalado

`log1p(x) = ln(1+x)`. En variables no negativas conserva cero, orden y una transformación reversible (`expm1`). Comprime diferencias grandes: 1→0,693; 10→2,398; 100→4,615. No impone techo ni elimina observaciones.

**Insight importante:** al ser estrictamente creciente, `log1p` preserva Spearman y AUC de rangos de una columna, salvo empates/precisión numérica. Por eso una AUC descriptiva idéntica antes/después **no demuestra que el log sea inútil**; cambia la relación funcional/escala para ciertos algoritmos. Tampoco usar “mejor Spearman” como criterio para aceptarlo. Un árbol de umbrales puede producir particiones equivalentes bajo transformaciones monótonas; el beneficio concreto depende de la implementación y se mide, no se presume.

| Técnica | Candidatas | Dónde / condición | Lo que no hace |
| :--- | :--- | :--- | :--- |
| log1p directo | BVP_std, EDA_median, dispersiones ACC. | Copia de 3.5/3.9; comparación con originales en sección 4. Confirmar no negativos/calidad. | No elimina artefactos ni balancea etapas. |
| log de magnitudes pequeñas | EDA_std y ciertas PSG_std. | Solo si hay justificación; declarar unidad o escala `s` en `log1p(x/s)`. Aprender `s` en entrenamiento si es empírico. | `log1p(1e-5)` casi no cambia `1e-5`; no aplicarlo por rutina. |
| Escalado estándar | Predictores continuos en un modelo sensible a escala. | Pipeline ajustado con pacientes de entrenamiento en cada partición. | No fuerza normalidad ni recorta. |
| Escalado robusto | Continuas con colas plausibles. | Mediana/IQR del entrenamiento; comprobar IQR cero o diminuto. | No limita valores extremos transformados. |
| Corrección de unidades | Solo canales con conversión confirmada. | Antes de agregar desde crudo; documentar y versionar. | No adivinar volts/µV ni dividir SAO2 aisladamente. |
| Imputación de señal | Solo si aparecen datos realmente inválidos/faltantes. | Regla según sensor/tiempo, preservando huecos y ajustando parámetros en entrenamiento cuando corresponda. | No rellenar etiquetas largas ni fabricar continuidad. |
| Clipping/binning | Sin justificación actual. | Eventual experimento específico; límites aprendidos solo en entrenamiento. | No es requisito por cola larga o desbalance. |

El escalado robusto centra con mediana y divide por rango de cuantiles; sus parámetros se estiman en entrenamiento y se reutilizan después. Puede dejar valores muy grandes si el IQR es pequeño. [Documentación de RobustScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html).

Una variable de PSG pequeña por su unidad no es inútil: cambiar unidad y escalar son formas diferentes de ajustar representación. Verificar metadatos porque las magnitudes observadas y las unidades resumidas de la fuente no bastan para aprobar una conversión automática.

### G.3. Reducciones y redundancia real

Ojos/piernas: máximo bilateral conserva la mayor actividad, pero puede privilegiar el canal ruidoso y perder asimetría. Alternativas: originales; máximo más diferencia absoluta; actividad de ambos lados; resumen robusto. Evaluar solo las que respondan una pregunta, no agregar todas por volumen.

ACC: `sqrt(std_X² + std_Y² + std_Z²)` resume dispersión de los tres ejes. Con la misma cobertura y calibración por eje equivale a la raíz de la traza de la covarianza y es invariante ante una rotación ideal. **No es** `std(sqrt(X²+Y²+Z²))`. Puede perder postura/dirección; la adquisición/cuantización real limita la invariancia ideal. Comparar contra los tres ejes y, si hay fuente fiable, contra una característica de magnitud cruda.

EEG: alta correlación no prueba que uno sea prescindible para N3/R. Comparar retiros alternativos con mismo algoritmo, mismos pacientes y ajuste independiente de hiperparámetros cuando sea pertinente. No retirar todas las columnas correlacionadas simultáneamente y atribuir después la mejora a una sola.

**Redundancias algebraicas que sí pueden dejarse fuera de X sin confundirlas con Spearman:**

- `missing_frac = 1 − n_valid/3000`: información equivalente bajo la definición actual de cobertura.
- Varianza = std²: no son dos señales diferentes.
- Una columna log y su original representan la misma medición con transformación invertible; comparar versiones antes de agregarlas juntas sin motivo.
- El tiempo ordinal y físico son casi equivalentes en tramos completos, pero dejan de serlo al recuperar segmentos; preferir tiempo físico.

No hace falta PCA ni una reducción masiva solo por tener 22/26 predictores y decenas de miles de epochs. La limitación estadística principal es la cantidad/heterogeneidad de pacientes y la dependencia temporal, no el tamaño de X por sí solo. PCA podría estudiarse después, con escalado/ajuste en entrenamiento y menor interpretabilidad como costo.

### G.4. Variables nuevas con una pregunta concreta

No están implementadas ni validadas. Prioridad propuesta:

| Familia | Candidatas | Para qué / condición |
| :--- | :--- | :--- |
| Calidad | Fracción plana, saltos, saturación, calidad multisensor; ID de segmento y continuidad. | Distinguir reposo de relleno y evitar ventanas cruzadas. Metadatos primero; uso predictor solo si existe al inferir. |
| EEG | Potencias por bandas, potencia relativa y relaciones entre bandas. | Capturar contenido frecuencial que std no conserva; verificar unidades, filtros y frecuencia disponible. |
| EOG / EMG | Actividad transitoria, amplitud robusta, diferencias bilaterales, características de forma/frecuencia. | Investigar REM/W sin reducir todo a máxima std; evitar considerar ruido como actividad. |
| ACC | Magnitud cruda, cambios, actividad por intervalos y postura si es consistente. | Describir movimiento y orientación por separado; confirmar unidades y remuestreo. |
| BVP / HR | Calidad de pulso, cambios de HR y características latido a latido si hay eventos fiables. | Complementar amplitud; no calcular HRV a partir de IBI congelado o repeticiones a 100 Hz. |
| EDA / TEMP | Cambio respecto de nivel reciente, pendiente, duración de episodios y componentes EDA si la calidad permite. | Reducir dependencia de nivel basal; definir ventana causal para uso en tiempo real. |
| Respiración | Periodicidad y coherencia tórax–abdomen, amplitud robusta. | Capturar patrón respiratorio en lugar de ganancia del sensor; resolver antes las escalas. |
| Contexto temporal | Resúmenes de señales de epochs previos válidos. | Capturar secuencia sin usar etiquetas verdaderas; no cruzar huecos ni pacientes. |

Con 100 Hz la frecuencia de Nyquist es 50 Hz, y las señales remuestreadas desde menor frecuencia no adquieren nuevo contenido hasta 50 Hz. No proponer características fuera del ancho de banda disponible ni tratar cambios artificiales del remuestreo como eventos nuevos. La extracción de características espectrales/dinámicas puede ser útil después de una referencia simple; no es condición para iniciar toda comparación futura.

## H. Desbalance: tratamiento y efectos

El desbalance tiene dos niveles: **epochs por etapa** y **pacientes que aportan esa etapa**. Multiplicar epochs de N3 no aumenta sus 35 personas observadas. La variación entre personas y el mínimo de cinco epochs explican que solo 26 sean evaluables en el contraste N3 de 3.5.1.

**No se normaliza `Sleep_Stage`.** Escalar predictores, dar igual peso a pacientes en un gráfico y balancear clases son operaciones distintas.

| Alternativa futura | Beneficio buscado | Costo / precaución |
| :--- | :--- | :--- |
| Sin balanceo | Referencia bajo frecuencias reales. | Puede favorecer N2. |
| Pesos de clase | Penalizar más errores de minoritarias sin fabricar filas. | Puede subir recuperación N3/R y también falsos positivos, bajar precisión y alterar calibración. |
| Sobremuestreo | Más exposición a minoritarias durante entrenamiento. | Repetir ventanas no crea pacientes; riesgo de sobreajuste temporal. |
| Submuestreo N2 | Menos dominio de la mayoritaria. | Descarta diversidad útil. |
| Peso por paciente | Evitar dominio de registros largos. | No es igual a peso de clase; combinarlos cambia el objetivo y necesita evaluación. |

La regla balanceada habitual usa `n/(k × n_clase)`. Como **ilustración aritmética no aplicada** sobre los recuentos amplios, los pesos serían W 0,903; N1 1,702; N2 0,388; N3 5,281; R 1,858. Los pesos reales deben calcularse nuevamente **solo con entrenamiento**, no tomar estos números para todas las particiones. [Documentación de pesos de clase](https://scikit-learn.org/stable/modules/generated/sklearn.utils.class_weight.compute_class_weight.html).

Mantener validación y prueba con frecuencias reales. Evaluar F1 macro, exactitud equilibrada, precisión/recuperación/F1 por etapa y matriz de confusión; acompañar con variación entre pacientes. Un promedio de métricas por paciente debe aclarar cómo trata etapas ausentes. Para probabilidades, estudiar calibración en datos no balanceados.

**Recomendación:** primera comparación sin pesos; luego pesos de clase. No empezar por SMOTE indiscriminado mezclando personas, tiempos y fisiología. Ninguna estrategia puede compensar etiquetas poco confiables o clases ausentes en demasiados pacientes.

## I. Qué está bien, qué corregir y qué no agrega valor ahora

| Prioridad | Hallazgo | Acción y criterio de cierre |
| :--- | :--- | :--- |
| Alta | Salidas 73/18 y documentos 76 mezclados. | Una ejecución y manifiesto identificables; todos los cuadros declaran la misma cohorte o justifican explícitamente un subconjunto. |
| Alta | `epoch` usado como reloj/continuidad en 3.6 y 3.3.1. | Tiempo real y segmento; prueba dentro del notebook que no cuente transiciones sobre huecos y conserve duración válida. |
| Alta | Escalas FLOW y otras amplitudes heterogéneas. | Metadatos/procedencia y reporte por paciente; corregir solo conversiones verificadas o declarar limitación y sensibilidad. |
| Alta antes de evaluar | Candidato pierde marcas de etiquetas inferidas. | Metadatos aparte o unión por clave/version; ninguna etiqueta imputada como verdad de prueba. |
| Media | Alineación especial solo para dos nombres; S077 no verificado. | Auditoría previa de nuevos archivos y tratamiento genérico con trazabilidad. |
| Media | Congelamiento BVP en casi todos los pacientes y segunda PSG plana. | Localizar intervalos/etapas y coincidencia multisensor; decidir con evidencia. |
| Media | Redondeos de PSG y tablas truncadas. | Precisión legible; tablas completas relevantes y resumen breve; no inferir cero/constancia por formato. |
| Media | Caché/versiones/tipos y costo de relectura. | Esquema explícito, huellas y checkpoints; probar caché y reconstrucción de forma diferenciada. |
| Posterior | EOG/piernas/ACC reducidos sin evaluación. | Ablación y métricas por etapa fuera de paciente; conservar originales. |
| Posterior | Frecuencia/morfología ausentes de características. | Agregar una familia por vez si la referencia evidencia una limitación concreta. |

**Bien hecho y para sostener:** fuente intacta, claves, ventana alineada, marcas de inferencia, reporte de descartes, análisis global y por paciente, categorías sin orden arbitrario, no clipping global, preservación de EEG correlacionado y separación entre controles técnicos/modelado.

**Poco útil o prematuro:** repetir matrices gigantes sin pregunta; generar gráficos de todos los pacientes sin priorizar; transformar toda variable sesgada para “hacerla normal”; mantener código de limpieza no utilizado como si actuara; agregar std y varianza como información distinta; decidir por AUC in-sample o Spearman; equilibrar el CSV completo; usar tiempo total/latencias/proporciones verdaderas como entradas; eliminar un paciente porque no muestra N3/R. Las dos representaciones base/candidata nunca se concatenan verticalmente como datos nuevos.

## J. Secuencia siguiente y guía para estudiar/exponer

### J.1. Pasos siguientes, sin entrenamiento realizado

1. **Fijar la versión:** recuperar dataset amplio, auditorías y manifiesto de la misma ejecución; corregir cifras documentales y el log S091/S095. No reconstruir por costumbre si la caché válida existe.
2. **Corregir temporalidad:** 3.6 y continuidad de 3.3.1; agregar segmento/intervalos cuando corresponda. Registrar pruebas dentro del notebook, incluyendo un hueco entre segmentos.
3. **Cerrar revisiones prioritarias:** FLOW y escalas respiratorias; BVP plano/bordes; segundo paciente con PSG plana; EDA/TEMP marcados. No exigir resolver cada IQR antes de continuar: conservar los casos inciertos con una limitación explícita.
4. **Regenerar resultados coherentes:** vista cruda, prueba temporal amplia, variantes, candidato, controles y diccionario. Comparar filas, claves, etapas, tiempos, cobertura y trazabilidad. Guardar salida ejecutada, no solo código nuevo.
5. **Acordar el uso:** PSG + wearable y wearable solo son escenarios distintos. Usar EEG/EOG para clasificar una etapa anotada mediante PSG es legítimo si esos canales existirán al inferir; no demuestra capacidad del wearable solo.
6. **Reservar pacientes de prueba:** antes de selección predictiva, escalado y tuning. Validar por grupos entre los restantes y verificar presencia de N3/R. `StratifiedGroupKFold` intenta conservar proporciones sin compartir grupos, pero no garantiza equilibrio perfecto cuando las clases se concentran en pocas personas. [Validación estratificada por grupos](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html).
7. **Implementar referencias en sección 4 cuando se autorice:** clasificador trivial, regresión logística multiclase regularizada y un árbol/ensemble como contraste. Misma partición y métricas; escalado solo donde sea pertinente.
8. **Comparar una decisión por vez:** señales/tiempo/señales+tiempo; originales/log; ojos, piernas, ACC; ablaciones EEG; pesos de clase; después familias nuevas. Registrar ventajas, pérdidas N3/R, costo y estabilidad. Una reducción no se acepta solo por pasar controles.
9. **Cerrar variables y modelo:** usar validación para decidir y prueba final una vez. Si la cohorte completa ya se exploró extensamente con sus etiquetas, reconocer que una reserva posterior no borra esa exposición; evitar decisiones adicionales guiadas por los pacientes de prueba y considerar evaluación externa futura.

**¿Puede avanzar a algoritmos?** Tiene una representación tabular adecuada para referencias, pero primero conviene resolver coherencia de salidas, temporalidad, procedencia y trazabilidad. Las dudas de sensores pueden quedar explícitas y estudiarse con sensibilidad; no hace falta agregar cien variables ni demostrar causalidad antes de una línea base. Todavía no existe evidencia para llamar “final” al candidato de 3.9.

### J.2. Ideas centrales para explicar con tus palabras

1. **Problema:** “Queremos clasificar cinco categorías de sueño por ventana de 30 segundos; no predecir una profundidad numérica”.
2. **Dato:** “Las filas originales son muestras de señales sincronizadas; las filas del ETL son epochs. Miles de muestras con la misma etapa no son miles de etiquetas independientes”.
3. **Transformación principal:** “Alineamos ventanas antes de filtrar y resumimos nivel, variación y cobertura; guardamos qué quedó fuera y por qué”.
4. **Calidad:** “No tener nulos no garantiza una señal válida; encontramos canales planos, unidades dudosas y tramos desalineados”.
5. **Evidencia fuerte:** “La dispersión EEG aumenta en N3 y el movimiento en W, con patrones consistentes entre pacientes; no es todavía rendimiento en personas nuevas”.
6. **Desbalance:** “N2 representa 51,54 % y N3 3,79 % en la salida amplia. Evaluaremos cada clase; acertar la mayoritaria no alcanza”.
7. **Reducciones:** “Ojos, piernas y acelerómetro tienen versiones resumidas candidatas; las originales siguen disponibles. La correlación no autoriza borrarlas”.
8. **Tiempo:** “Existe asociación antes/después, pero depende de la persona y la cobertura. Usamos tiempo real; el número de epoch no reemplaza un reloj con huecos”.
9. **Modelo futuro:** “Separaremos pacientes y ajustaremos transformaciones aprendidas dentro de entrenamiento; compararemos referencia original con cada cambio”.
10. **Honestidad del estado:** “El archivo mezcla salidas amplias y temporales menores; hay que regenerar una corrida coherente antes de presentar cifras como una única ejecución”.

### J.3. Preguntas previsibles y respuestas breves

- **¿El boxplot muestra la noche?** No. En 3.3 compara características de epochs por etapa; en 3.6 compara porcentajes por paciente. El hipnograma y los bloques temporales sí muestran secuencia/tiempo.
- **¿Un rojo es un error?** No: es una marca de revisión manual o estadística, según la figura.
- **¿Por qué no borrar los outliers?** Porque varias marcas corresponden a las diferencias que distinguen W/N3; falta evidencia de defecto y podría empeorar el desbalance.
- **¿Por qué std en una onda?** Porque la media puede cancelar oscilaciones y std describe amplitud. Pierde frecuencia/forma; no es superior para todas las señales.
- **¿Qué hace el log?** Comprime escala y conserva orden; no corrige ni corta la señal.
- **¿Qué hace el escalado?** Cambia centro y unidades relativas para el algoritmo. No balancea etiquetas ni impone techo.
- **¿Por qué ID aparece muchas veces?** Porque cada paciente aporta muchas ventanas; la clave es paciente+epoch, no paciente solo.
- **¿AUC 0,89 es 89 % de aciertos?** No. Describe ordenamiento de valores etapa/resto; aquí no evaluó un modelo fuera de muestra.
- **¿Correlación 0,93 significa borrar un EEG?** No. Primero comprobar aporte incremental mediante ablación y efecto sobre N3/R.
- **¿Los blancos de EDA son señal faltante?** No necesariamente; en S027/S048 son principalmente tiempo sin epochs retenidos por alineación.
- **¿Ya se aplicó el candidato?** Sí, está comprobado en los CSV de 18 pacientes; su utilidad y aplicación amplia coherente siguen pendientes. No modifica el ETL base.
- **¿Ya se entrenó algo en esta versión?** No. Los controles son de construcción y las AUC son descriptivas; los algoritmos están propuestos en sección 4.

### J.4. Qué se modificó y qué se verificó en esta revisión

Se actualizó **solo este resumen**. No se modificaron el notebook, los CSV, sus reglas, etiquetas ni la selección; no se entrenaron algoritmos y no se hizo commit/push. La guía del TP orientó a separar comprensión/ETL de evaluación predictiva y a justificar cada propuesta, sin ejecutar transformaciones nuevas sobre los datos.

Verificaciones actuales: sintaxis de las 39 celdas no vacías; inspección de 163 salidas y 28 figuras; claves e identidad base/candidato de 18 pacientes; 14 variantes construidas en memoria; concordancia de las 22 fórmulas de la candidata con su CSV; reproducción del defecto temporal mediante el código existente. **No se realizó una nueva ejecución integral ni una reconstrucción de los 74 archivos.** Los defectos documentados requieren cambios posteriores autorizados y pruebas registradas en el notebook.

La huella SHA-256 del notebook revisado es `6378d04a41c4f81e533b490fbb10833819e440cc0ca0dc89b0fb254493e7113e`. Permite distinguir este adjunto de versiones con otros recuentos. Este resumen es material de estudio y discusión: separa lo observado, sus límites y las decisiones que todavía hay que medir.
