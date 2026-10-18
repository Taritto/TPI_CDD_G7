# Plan de limpieza y estructura del notebook

## 1. Objetivo y ejecución de referencia

Simplificar [temporal_version_tp_cdd.ipynb](../temporal_version_tp_cdd.ipynb) para que el equipo pueda entender qué se analizó, qué decisiones se tomaron, qué dataset se obtiene y qué falta antes de modelar.

La referencia acordada es la ejecución de **77 archivos auditados, 76 pacientes incluidos y 56.850 epochs**. Los resultados de 74 archivos/73 pacientes/54.367 epochs y las salidas de 18 pacientes corresponden a otras ejecuciones: no se usarán para fundamentar las conclusiones de esta versión.

Estas cifras fijan la ejecución que se debe recuperar y verificar; no justifican agregar, repetir o eliminar registros para hacer coincidir los conteos. El dataset, las auditorías, el manifiesto y las salidas deben corresponder a esa misma ejecución.

**Estado:** limpieza y correcciones implementadas; validación completa de la ejecución de referencia pendiente. El notebook pasó de 93 a 63 celdas. Las salidas históricas mezcladas se retiraron; deben regenerarse con los artefactos de los 77 archivos.

### Relación con los documentos existentes

- [Guía del notebook](guia-resumen-notebook.md): explica los análisis y ayuda a estudiarlos.
- [Estado y próximos pasos](estado-actual-y-proximos-pasos.md): comunica el avance y las tareas pendientes; debe actualizarse a la ejecución de referencia.
- [Plan de transformación](plan-ejecucion-transformacion.md): conserva las decisiones y alternativas sobre variables, transformaciones y evaluación futura.
- **Este documento:** define cómo corregir, reducir y ordenar el notebook. No reemplaza ni duplica el plan de transformación.

## 2. Criterios para decidir qué queda

Cada tabla o gráfico debe responder una pregunta y permitir una conclusión o decisión concreta. Si repite información ya mostrada, se elimina la salida redundante o se integra con otra.

- Conservar resúmenes globales, incidencias relevantes y evidencias que fundamentan decisiones.
- No confundir simplificar el notebook con eliminar datos del dataset.
- Mantener las tablas completas de auditoría en los archivos correspondientes; mostrar en el recorrido principal un resumen y las incidencias. El detalle debe seguir siendo accesible, no perderse silenciosamente.
- Mantener una vista cruda breve para explicar la diferencia entre la señal y sus resúmenes por epoch. Identificar al paciente y aclarar que no representa toda la cohorte.
- Dejar inspecciones extensas como diagnóstico opcional dentro del mismo notebook, cuando sean necesarias para rastrear un problema.
- No entrenar algoritmos como parte de esta limpieza.

En la versión inspeccionada había 93 celdas, 52 tablas HTML y 28 imágenes. El archivo pesaba 4,45 MB y aproximadamente el 85 % correspondía a imágenes guardadas. La mayor reducción de tamaño se logrará quitando figuras repetidas, no solamente acortando textos.

## 3. Correcciones prioritarias

### 3.1. Unificar el alcance de las salidas

Recuperar los artefactos de la ejecución de referencia y regenerar las salidas del notebook sobre ellos. El análisis temporal, la revisión de variables y el candidato de modelado deben usar los mismos 76 pacientes y 56.850 epochs, salvo exclusiones descriptivas explícitas y justificadas.

Mostrar al comienzo del resultado del ETL una ficha calculada durante la ejecución: archivos auditados, incluidos/excluidos, pacientes, epochs, columnas, etiquetas imputadas y descartes. Evitar repetir cifras escritas manualmente en varias secciones.

Actualizar las conclusiones y los dos documentos de resumen a partir de esa ficha. No trasladar porcentajes o cantidades de etapas desde una ejecución anterior.

### 3.2. Usar tiempo real en lugar del número de epoch

En **3.6**, corregir el cálculo de latencia REM observada, extensión del tramo observado, huecos y transiciones contiguas. Usar `tiempo_relativo_segundos`, porque el número de epoch puede seguir siendo consecutivo después de recuperar fragmentos separados.

- Duración válida: cantidad de epochs conservados × 30 segundos. Esta definición se mantiene.
- Tramo observado: tiempo entre el inicio del primer epoch y el final del último; puede incluir huecos.
- Latencia REM observada: diferencia temporal entre el primer sueño observado y el primer REM observado, si existen ambos.
- Continuidad: verificar separación de 30 segundos entre inicios de epochs, con tolerancia numérica, sin conectar fragmentos separados.

En **3.3.1**, aplicar el mismo criterio a vecinos y tramos de candidatos atípicos. No tratar dos epochs consecutivamente numerados como vecinos temporales si existe un hueco real.

La latencia es descriptiva del registro disponible; no debe presentarse como una medición clínica completa cuando faltan tramos.

### 3.3. Separar implementación, ejecución y validación

La existencia del código o de un diccionario guardado no demuestra que el candidato se haya exportado sobre toda la cohorte. Regenerar conjuntamente las salidas de construcción, controles, exportación y diccionario final.

Usar términos claros: **implementado**, **ejecutado**, **controlado estructuralmente** y **pendiente de evaluación predictiva**. Pasar controles no demuestra que una transformación mejore un modelo.

## 4. Cambios por sección

| Sección actual | Qué se hará | Qué debe conservarse |
| --- | --- | --- |
| 2.1–2.3: exploración de tres pacientes | Sustituir tablas repetidas por una ficha de estructura y diferencias relevantes. | Significado de señales, grano, tipos e incidencias; alcance de la muestra. |
| 2.2.1–2.2.2: clases y comparaciones individuales | Quitar del recorrido principal los gráficos repetidos de la muestra. | Distribución de clases del ETL completo y análisis entre pacientes. |
| 2.3.1: mínimos y máximos de muestra | Retirar la inspección genérica extensa. | Una demostración cruda breve y los casos que justifican revisión. |
| 2.4–2.5: epochs e hipnograma | Evitar una segunda implementación del agregado; conservar un hipnograma ilustrativo. | Explicación de ventanas de 30 segundos, etapas y continuidad real. |
| 2.6: auditoría global | Compactar salidas en una tabla de incidencia, evidencia, decisión y pendiente. | Motor de auditoría, trazabilidad, alineación, constantes, SAO2/IBI y archivos completos. |
| 2.6.4: revisión EDA | Reducir figuras a las necesarias para justificar las incidencias. Dejar ventanas adicionales como diagnóstico opcional. | Casos relevantes, contexto temporal y distinción entre sospecha y defecto confirmado. |
| 3.2: resultado ETL | Mostrar ficha global y resumen de incluidos, parciales, excluidos, imputaciones y descartes. Compactar el diccionario base por familias. | Artefactos de auditoría y explicación del dataset de epochs. |
| 3.3–3.3.2: distribuciones | Unificar boxplots repetidos y tablas de cobertura. Seleccionar histogramas que expliquen asimetría. | Desbalance, distribuciones prioritarias y vista cruda individual breve. |
| 3.3.1: candidatos atípicos | Mantener un resumen por variable. Pasar listas extensas de casos, pacientes y tramos a detalle opcional. | Criterio IQR, denominadores, marcas y aclaración de que no se recortan datos. |
| 3.3.3: EDA por paciente | Evitar mostrar tabla completa y varias figuras que comunican lo mismo. | Vista temporal útil, resumen de pacientes marcados y explicación de bloques sin epochs retenidos. |
| 3.4: asociaciones | Priorizar tabla de pares altamente correlacionados y mapa de asociación con etapas. Pasar mapas secundarios a detalle opcional. | Correlación no implica prescindibilidad; AUC descriptiva no es rendimiento de un modelo. |
| 3.4.3: tiempo–etapa | Conservar proporción global, promedio por paciente y cobertura. Sustituir tabla/mapa extensos individuales por un resumen de estabilidad. | Pacientes evaluables, dirección temporal, heterogeneidad y cobertura decreciente. |
| 3.5: variables y variantes | Reemplazar la ficha extensa y el despliegue de 14 variantes por una tabla de decisiones y alternativas. | Función necesaria para construir el candidato y propuestas de ablación futura. |
| 3.6: resumen por paciente | Corregir el reloj; conservar tabla agregada y gráficos principales. Mostrar detalle individual solo cuando sea necesario. | Proporciones, duración válida, latencia observada y etapas no observadas. |
| 3.7–3.9: controles y exportación | Consolidar controles y evitar tablas duplicadas. | Transformaciones candidatas, exportación validada y diccionario final por columna. |
| 4–7: etapas futuras | Mantener una sola sección de próximos pasos; quitar encabezados y celdas vacíos. | Plan de modelado y reevaluación posterior, sin ejecutar algoritmos. |

### Referencias después de renumerar

La tabla anterior identifica las secciones de la versión previa. En la versión simplificada, la auditoría cruda pasa de **2.6 a 2.2** y sus apartados mantienen el orden de alineación, SAO2, constantes y EDA. La asociación con etapas queda en **3.4.1** y la relación tiempo–etapa en **3.4.2**. Se retira la demostración sintética de 3.5.3; los controles reales del candidato permanecen en **3.9**, con el diccionario final en **3.9.1**. Los próximos pasos se concentran en **4**; se eliminan las secciones vacías 5–7.

## 5. Pruebas y código: qué quitar y qué mantener

### Quitar del recorrido principal

- Demostraciones con datos inventados de la prueba temporal y de identidad/exportación de CSV.
- Tablas repetidas de controles y listados completos de variantes no evaluadas.
- Funciones `clean_sleep_stages`, `clean_sao2`, `clean_outliers_wearable_psg` y `run_etl_pipeline`, si al implementar se confirma que siguen sin uso y sin limpieza efectiva.
- Código comentado obsoleto, celdas vacías y relatos sobre versiones anteriores que no ayudan a interpretar la versión vigente.

Antes de retirar una celda, comprobar qué funciones y variables usan las siguientes. En particular, **3.9 depende de `construir_predictores`, definida en 3.5.2**: simplificar 3.5 no debe romper esa dependencia.

### Mantener como controles sobre datos reales

- Unicidad de `(patient_id, epoch)` y de los instantes dentro de cada paciente.
- Etiquetas válidas y finitud de los predictores seleccionados.
- Conciliación de filas fuente, fragmentos, epochs conservados y descartados.
- Igualdad de claves, pacientes, etiquetas y recuentos antes/después de la transformación candidata.
- Comprobación de las fórmulas de transformación y preservación del ETL base.
- Validación de los CSV antes de exportar o reutilizar la caché.

Los controles permanecerán dentro del notebook, con una tabla breve de resultado e incidencia. Una falla relevante debe detener la exportación; no basta con imprimir una advertencia. No se crearán tests externos.

## 6. Estructura y redacción previstas

Mantener una separación visible entre **EDA crudo**, **ETL**, **análisis del dataset de epochs**, **transformación candidata** y **modelado futuro**. Renumerar subsecciones y referencias cuando se retiren bloques.

Cada bloque tendrá tres elementos breves:

1. Qué pregunta se busca responder.
2. Qué muestra la evidencia de la ejecución de referencia.
3. Qué decisión permite tomar y qué queda pendiente.

Reglas de presentación:

- Una salida principal por pregunta; las salidas complementarias deben aportar algo distinto.
- Tablas resumidas con nombres y denominadores claros. Por ejemplo, cambiar `porcentaje_validos` por `porcentaje_epochs_marcados` cuando realmente mide candidatos entre epochs válidos.
- Notación científica para amplitudes pequeñas; no mostrar valores distintos de cero como `0.00`.
- Informar cuándo se ocultan puntos extremos de un boxplot. Ocultarlos visualmente no elimina datos.
- Aclarar si una figura usa `log1p` solo para visualizar o si muestra columnas transformadas del candidato.
- En gráficos temporales, conservar la cobertura y distinguir el peso por cantidad de epochs del peso igual por paciente. No son dos estimaciones intercambiables.
- Quitar conclusiones pendientes de redactar, explicaciones repetidas y afirmaciones de calidad no sustentadas.

## 7. Límites: decisiones que esta limpieza no toma

- No elimina pacientes, epochs o columnas del ETL base por razones de presentación.
- Conserva `patient_id`, `epoch` y `tiempo_relativo_segundos` como trazabilidad. Su presencia en el archivo no implica que entren como predictores.
- Mantiene `Sleep_Stage` como objetivo categórico; no lo normaliza ni cambia el desbalance de clases.
- No aplica recorte global de outliers, binning ni imputación nueva de señales.
- No elimina canales PSG automáticamente por Spearman alto.
- Conserva los resúmenes de ojos, piernas y ACC y `log1p` como representaciones candidatas reversibles, no como mejoras demostradas.
- No trata la exclusión de SAO2/IBI de los predictores como una reparación de sus señales.

La sección de próximos pasos mantendrá las comparaciones entre representaciones originales y candidatas, ablaciones de PSG, tiempo como predictor y escenarios PSG + wearable/wearable solo. El modelado posterior deberá dividir por paciente y ajustar escalado o pesos de clase solo en entrenamiento, manteniendo las proporciones reales en validación y prueba.

## 8. Secuencia de implementación y aceptación

- [ ] Recuperar dataset, auditorías y manifiesto de los 77 archivos, 76 pacientes y 56.850 epochs; verificar su correspondencia.
- [ ] Registrar una línea de base de la cohorte de referencia: claves, recuentos por paciente/etapa, columnas y reglas vigentes.
- [x] Corregir cálculos temporales de 3.6 y continuidad de vecinos/tramos de 3.3.1, sin cambiar los datos base.
- [x] Eliminar duplicaciones, código sin uso, demostraciones sintéticas del recorrido principal y secciones vacías; preservar dependencias y controles reales.
- [x] Reorganizar tablas y figuras, simplificar textos y conservar acceso a auditorías completas.
- [ ] Regenerar resultados del candidato y su diccionario; distinguir exportación controlada de evaluación predictiva pendiente.
- [x] Actualizar la guía, el estado y las referencias del plan de transformación a la estructura nueva, separando la ejecución de referencia de la verificación parcial.
- [ ] Ejecutar de principio a fin desde un kernel limpio y verificar los controles dentro del notebook.

**Aceptación:** notebook ejecutable sin dependencia de variables de sesiones anteriores; salidas coherentes con la ejecución de referencia; dataset base y recuentos de clases preservados; correcciones temporales verificadas; CSV candidatos con claves únicas; cada sección con conclusión comprensible y pendientes explícitos. Medir el tamaño y las salidas finales, sin sacrificar evidencia necesaria únicamente para reducir bytes.

Si no están disponibles los artefactos de esa ejecución, dejar pendiente su validación completa. No reemplazarla por salidas de otra cohorte ni afirmar que el notebook completo fue verificado.

### Verificación realizada

Formato nbformat y sintaxis de las 28 celdas de código verificados. La entrada incompleta se bloquea con la configuración normal. En una sesión diagnóstica, utilizando la caché disponible de 18 pacientes y 13.165 epochs, se ejecutaron los análisis posteriores al ETL, los gráficos y los 12 controles del candidato. Se obtuvo un candidato de 26 columnas, con 22 predictores. También se ejecutó la auditoría completa de S002, con 1.958.400 muestras, y sus ramas opcionales de alineación e inspección EDA. Las exportaciones de verificación se realizaron en directorios temporales; los CSV originales quedaron idénticos.

Esta comprobación no certifica los 76 pacientes de referencia ni sustituye la reconstrucción de los 77 archivos. Las verificaciones de datos y exportación permanecen implementadas dentro del notebook; no se agregaron archivos de tests externos. La retirada de salidas históricas contribuye al menor tamaño actual; después de ejecutar, el archivo crecerá con las figuras relevantes regeneradas.
