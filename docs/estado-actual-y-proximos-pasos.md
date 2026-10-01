# Estado actual del dataset de sueño y próximos pasos

Resumen para discutir el paso del EDA/ETL al modelado. El detalle metodológico está en el [resumen del EDA y ETL](resumen-eda-y-etl.md), el [plan de transformación](plan-ejecucion-transformacion.md) y el [notebook](../temporal_version_tp_cdd.ipynb).

## Qué se hizo

- Se auditó la estructura de los CSV de DREAMT, las etapas anotadas, los rangos, los faltantes, la alineación temporal y señales que requieren revisión. Los valores atípicos se marcaron para inspección; no se recortaron globalmente.
- Se construyó un dataset supervisado de **una fila por epoch completo de 30 segundos**, con etapa, identificadores, tiempo relativo, resúmenes de señales y marcas de calidad. El ETL deja trazabilidad de descartes e imputaciones y usa una caché con manifiesto para evitar releer los CSV crudos cuando no cambiaron.
- En la ejecución completa guardada en el notebook se auditaron **74 archivos**, se incluyeron **73 pacientes** (71 completos y S027/S048 parcialmente) y se obtuvieron **54.367 epochs**. S097 se excluyó por señales PSG constantes. Se imputó una etiqueta `Missing` aislada en cada uno de S089, S095 y S096 cuando sus vecinos válidos coincidían; no se rellenaron tramos largos o ambiguos.
- Se analizaron distribuciones, desbalance de etapas, diferencias entre pacientes, asociaciones descriptivas y redundancia entre señales. N2 representa aproximadamente **51,5 %** de los epochs; N3, **3,8 %**. En los epochs conservados, 38 de 73 pacientes no presentan N3 observado y 12 no presentan REM observado. Esto no implica ausencia fisiológica de esas etapas.
- Se definieron variantes reversibles de características y una **copia candidata** de modelado: `log1p` para BVP/EDA y el resumen ACC, máximo bilateral de ojos y piernas, y norma de las desviaciones ACC. Las columnas originales permanecen en el ETL base. Los controles de construcción no demuestran que esa copia mejore la clasificación.

**Alcance comprobado:** las salidas guardadas documentan la cohorte de 73 pacientes, pero el CSV cacheado disponible localmente contiene **13.165 epochs de 18 pacientes**. La sección 3.9 no tiene una salida guardada de la ejecución completa. **La versión actual del notebook no contiene un entrenamiento ni una evaluación de algoritmos.**

## Qué falta antes de evaluar modelos

1. Recuperar juntos el CSV completo de 54.367 epochs, el manifiesto y las auditorías; ejecutar de principio a fin los controles de 3.7 y las transformaciones candidatas de 3.5/3.9. Confirmar filas, pacientes, clases, claves y valores finitos sin usar la caché reducida para conclusiones globales.
2. Cerrar o dejar explícitamente marcadas las incidencias pendientes: segmentos excluidos de S027/S048, EDA elevada en S004/S057/S027, temperatura baja y escala/calidad de SAO2 e IBI. No corregir una señal ni eliminar pacientes por un máximo o por la regla IQR sin evidencia localizada.
3. Acordar el escenario de uso: **PSG + wearable** o **wearable solo**. Son preguntas distintas; las señales PSG pueden no estar disponibles en la aplicación final.

## Primera etapa de modelado propuesta

1. Reservar pacientes para una **prueba final intacta** y validar dentro de los restantes, sin compartir pacientes entre particiones. `patient_id` agrupa la división, pero no entra en `X`; `Sleep_Stage` es el objetivo.
2. Implementar primero un clasificador trivial como referencia; después comparar una regresión logística multiclase y un modelo no lineal de árboles. Ajustar cualquier escalado y calcular posibles pesos de clase **solo con los pacientes de entrenamiento**.
3. Con las mismas particiones, contrastar señales originales frente a las transformaciones candidatas, el uso de `tiempo_relativo_segundos`, las reducciones de ojos/piernas/ACC y ablaciones alternativas de canales PSG correlacionados. Una correlación alta no autoriza descartar una columna automáticamente.
4. Comparar matriz de confusión, F1 macro, precisión y recuperación por etapa —en especial N3 y REM—, además de la variación entre pacientes. Mantener las proporciones reales en validación y prueba. Revisar errores para decidir cambios puntuales en el **dataset candidato**, sin alterar el ETL base ni consultar repetidamente la prueba final.

**Criterio de avance:** una transformación se acepta por mejora estable en pacientes no vistos y ausencia de deterioro relevante en etapas minoritarias, no porque pase controles estructurales o mejore solo la exactitud global. Si la calidad de una señal sigue incierta, informar la limitación y comparar resultados con y sin el tramo afectado antes de decidir una corrección.
