# Resumen del EDA y del ETL de etapas del sueño

**Para discusión del equipo.** Fuente de trabajo: CSV por paciente de DREAMT 2.2.0 y [notebook principal](../temporal_version_tp_cdd.ipynb). Objetivo: construir una tabla supervisada para clasificar `Sleep_Stage` en **W, N1, N2, N3 y R** usando señales de PSG y wearable. El registro está a 100 Hz; un epoch de 30 segundos reúne 3000 filas crudas. **La etapa es categórica:** REM no es un nivel más profundo que N3.

**Alcance de los resultados:** el equipo comunicó una ejecución amplia de **74 archivos auditados, 73 incluidos** (71 completos y 2 parciales), S097 excluido y **54.367 epochs** supervisados. Esos recuentos corresponden a esa ejecución y pueden cambiar si se agregan archivos. El cache que está en este repositorio conserva **13.165 epochs de 18 pacientes**; no debe usarse para reemplazar los resultados amplios. Las salidas guardadas del notebook también pueden ser antiguas: comprobar la cohorte que imprime cada celda antes de citarlas.

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
| 3.3–3.3.3 | Describe proporciones de etapas, distribuciones de variables, candidatos IQR y EDA por paciente y tiempo. | Señala posibles artefactos o episodios reales; **no** aplica clipping, binning ni eliminación automática. |
| 3.4–3.4.3 | Calcula Spearman entre predictores, asociación univariada de cada señal con etapas mediante AUC de rangos y prueba descriptiva de `tiempo_relativo_segundos` por paciente/bloque. | Prioriza preguntas para modelado; no demuestra causalidad ni rendimiento en pacientes nuevos. La prueba temporal ejecutada localmente fue de 18 pacientes: N3 tiende a tiempos anteriores y R posteriores, pendiente de repetición amplia. |
| 3.5–3.5.4 | Informa cobertura y consistencia por paciente, redundancias, dominio de transformaciones y crea en **una copia en memoria** candidatos `log1p`, máximo bilateral ojos/piernas y norma ACC. | No borra columnas originales, no modifica `df_epochs_all` ni genera un nuevo CSV definitivo. |
| 3.6–3.8 | Resume etapas, REM y transiciones por paciente; controla rangos lógicos; documenta decisiones y pendientes. | Auditoría descriptiva y plan de preparación para modelado. Las secciones 4–7 siguen sin modelo ni resultados definitivos. |

**Clases en la ejecución amplia informada:** W 12.047 (22,2 %), N1 6.389 (11,8 %), N2 28.020 (51,5 %), N3 2.059 (3,8 %) y R 5.852 (10,8 %). N3 apareció en 35 pacientes y R en 61. El desbalance se **conserva** en el dataset; sus efectos se tratarán al evaluar modelos, no fabricando filas en el ETL.

**Fuera de las características actuales:** SAO2 e IBI por disponibilidad/calidad no resuelta; anotaciones de apnea porque son eventos clínicos y no predictores principales. Se conservan en el origen. No hay recorte global de extremos ni interpolación automática de señales. Los metadatos de pureza, cobertura e imputación se mantienen para auditoría; no se proponen como predictores iniciales.

## C. Qué está cerrado y qué falta

| Estado | Decisión o tarea |
| :--- | :--- |
| **Hecho** | Existe la transformación crudo → epochs de 30 segundos, un dataset consolidado, caché, trazabilidad de descartes, reglas de imputación aislada y recuperación parcial documentada. EDA, atípicos, clases y asociaciones tienen análisis descriptivo. |
| **Verificar en la cohorte definitiva** | Conciliar S027/S048 y las imputaciones con la auditoría; ejecutar y registrar 3.7; repetir 3.4.3 y 3.5.1–3.5.3 con los 73 pacientes o la cohorte final. Una celda ejecutada con 18 pacientes no cierra una conclusión de 73. |
| **Revisión dirigida, sin limpieza aprobada** | Decidir si EDA S004/S057 y TEMP baja son variación plausible o fallas localizadas; contrastar señal cruda, duración, unidades y cobertura. Si no se confirma defecto, conservar con marca. |
| **Pendiente de modelado** | Elegir escenario PSG + wearable o wearable solo; separar entrenamiento/validación/prueba por paciente; comparar señales, tiempo y señales + tiempo; probar transformaciones y reducciones contra originales; evaluar N3/R y ponderación de clases. No hay algoritmo entrenado ni selección final. |

**Acuerdo recomendado para el equipo:** conservar íntegro el dataset base y documentar cualquier corrección de fuente; retirar columnas únicamente de una copia de modelado y después de una comparación por paciente. El próximo artefacto a debatir es el [plan ejecutable](plan-ejecucion-transformacion.md), que indica qué dejar fuera de `X`, qué transformar/resumir y la evidencia necesaria para aceptar o rechazar cada cambio. Hasta disponer de la ejecución amplia de las nuevas celdas y del control 3.7, esas decisiones siguen **provisionales**.
