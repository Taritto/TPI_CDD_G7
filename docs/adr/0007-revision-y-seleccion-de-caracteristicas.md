# Revisión y selección de características

**Estado de implementación:** parcial. La sección 3.5.1 del notebook genera una ficha por característica con cobertura, pacientes con valor, variación, asociación descriptiva máxima por etapa y marca para revisar medias/medianas de señales oscilatorias. Todas las decisiones de inclusión en el modelo quedan pendientes. También resume, para variables prioritarias, la dirección de la diferencia de medianas entre una etapa y el resto dentro de cada paciente, exigiendo al menos cinco epochs válidos por grupo; los casos no evaluables permanecen faltantes. Se verificaron sintaxis y lógica con datos sintéticos. Falta ejecutar e interpretar estas tablas con los pacientes definitivos y comparar modelos mediante ablación. No se eligieron ni eliminaron columnas del dataset o del modelo.

Se conservarán en el dataset base los resúmenes calculados por epoch y los indicadores de calidad. La selección de predictores se hará en una copia para cada experimento. Una media o mediana cercana a cero en una señal oscilatoria puede deberse a compensación de valores positivos y negativos; no convierte en inútil a la señal completa. `HR_mean`, `TEMP_mean` y, sujeto a calidad/disponibilidad, `SAO2_mean` describen un nivel interpretable y no se descartan con ese argumento. Las medias/medianas de señales oscilatorias quedan **marcadas para revisión**, no eliminadas automáticamente.

## Cómo observar la relación con `Sleep_Stage`

No generar un gráfico de dispersión por cada columna numérica: el objetivo es categórico y habría demasiados gráficos poco legibles. Usar un conjunto limitado de diagramas de caja/violín o curvas de densidad por etapa para características prioritarias, con cantidad de epochs y pacientes por clase. Para explorar muchas columnas a la vez, usar el mapa de asociación por etapa descrito en la decisión 0006 y una tabla resumida de cobertura, dispersión y posible separación. Graficar en detalle solo las candidatas más prometedoras, las dudosas y las que presenten anomalías. Una diferencia visual es una hipótesis, no una prueba de capacidad predictiva; una superposición tampoco demuestra inutilidad conjunta.

## Estabilidad entre pacientes

Primero observar el comportamiento global; luego, **solo para variables candidatas a una decisión relevante**, comparar el patrón entre pacientes sin producir un gráfico completo por cada persona. Usar un resumen compacto paciente × etapa (por ejemplo, medianas o diferencias entre etapas, junto con número de epochs) para distinguir un patrón reproducible de uno dominado por pocos pacientes. Si una etapa está ausente o tiene muy pocos epochs en un paciente, marcarla como no evaluable para esa comparación, no como cero. Revisar también cobertura y calidad por paciente.

## Utilidad incremental en el modelo

Comparar un modelo de referencia con versiones que agreguen o retiren características o familias de señales (ablación), manteniendo la misma partición por paciente y el mismo procedimiento de entrenamiento. Imputación, escalado, selección y cualquier transformación basada en datos se ajustarán solo con pacientes de entrenamiento; usar validación por paciente para decidir y dejar una prueba final separada. Observar métricas por clase —en especial las minoritarias— y no solo exactitud global. Una diferencia pequeña o inestable entre particiones no justifica una poda concluyente. Correlación alta o asociación univariada con una etapa no garantizan aporte incremental.

## Regla de decisión

Para cada columna candidata, registrar significado físico, unidad, cobertura/calidad, variación, patrón global y entre pacientes, redundancia y resultado de la comparación de modelos. Clasificarla como **conservar**, **revisar** o **excluir del conjunto de predictores** con motivo explícito. No eliminarla del dataset base por comodidad ni para alcanzar un número arbitrario de columnas. El requisito de dimensiones del dataset entregable se verificará por separado del número de predictores del modelo.
