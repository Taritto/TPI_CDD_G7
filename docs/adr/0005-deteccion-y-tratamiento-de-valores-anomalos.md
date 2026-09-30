# Detección y tratamiento de valores anómalos

**Estado de implementación:** diagnóstico ampliado, tratamientos pendientes. La sección 3.3.1 conserva el IQR global y ahora muestra límites con ocho cifras significativas, tres pacientes y tres tramos consecutivos prioritarios por variable, y cinco casos extremos por variable. Aclara que las cajas de 3.3 aplican IQR por etapa, por lo que sus puntos no coinciden necesariamente con la tabla global. Las tablas completas permanecen en memoria. Se verificó la lógica con datos sintéticos, incluido IQR nulo; falta ejecutar e interpretar el reporte con los pacientes reales. No cambia el dataset ni aplica recortes, imputaciones, binning o exclusiones.

## Alcance y orden de revisión

1. **Integridad del ETL:** comprobar continuidad de `TIMESTAMP`, longitud/alineación de epochs, duplicados de `(patient_id, epoch)`, etiquetas válidas, tipos y cobertura de muestras por señal. Distinguir ausencias del dato de ceros medidos.
2. **Validez de la medición:** contrastar unidades, escala y límites instrumentales documentados para cada señal. Antes de llamar imposible a un valor, verificar la unidad del archivo original y la transformación aplicada. Los resúmenes de señales oscilatorias (por ejemplo, `BVP_mean` cercano a cero) no son inválidos solo por estar cerca de cero.
3. **Extremos estadísticos:** visualizar distribuciones globales por señal y etapa, proporción de valores señalados y pacientes que los aportan. Las reglas como IQR o percentiles sirven para **marcar candidatos**, no para borrar o truncar. No utilizar un umbral universal entre señales con escalas distintas.
4. **Contexto:** para los candidatos relevantes, inspeccionar epochs vecinos del mismo paciente, evolución temporal, cobertura/calidad, coherencia entre señales y eventual cambio de `Sleep_Stage`. Un pico aislado merece una lectura distinta de una elevación sostenida.
5. **Decisión trazable:** clasificar cada patrón como error confirmado, probable artefacto, extremo plausible o caso no resuelto. Registrar variable, criterio, cantidad de epochs/pacientes afectados, evidencia y tratamiento propuesto. Conservar el dato fuente y comparar dimensiones/calidad antes y después de cualquier transformación autorizada.

## Criterios iniciales por familia

- **`HR`, `IBI`:** revisar unidades, ceros, faltantes, cobertura y coherencia temporal; valores extremos pueden ser fisiológicos, de algoritmo del dispositivo o errores. No fijar todavía umbrales clínicos.
- **`SAO2`:** verificar si la escala es fracción o porcentaje y si el sensor entrega valores fiables. Un rango físico solo puede aplicarse tras confirmar escala y procedencia.
- **`TEMP`, `EDA`:** comprobar unidades, cambios bruscos, mesetas y diferencias entre pacientes; no exigir distribución normal ni imponer rangos arbitrarios.
- **`BVP` y `ACC_X/Y/Z`:** revisar saltos, saturación, señal plana y coincidencia entre `BVP_std` extremo y movimiento. El acelerómetro ayuda a sospechar artefactos, no los confirma por sí solo.
- **Señales PSG oscilatorias:** medias próximas a cero pueden resultar de compensación de fases; examinar dispersión, amplitud/cobertura y plausibilidad antes de descartar columnas.
- **Anotaciones de apnea:** son eventos y quedan fuera de los predictores principales según la decisión previa; no tratarlas como mediciones continuas sujetas a recorte de extremos.

## Reglas de tratamiento pendientes de evidencia

Un error confirmado puede motivar marcar el dato como faltante o excluir el epoch afectado; un artefacto probable puede justificar indicador de calidad, exclusión puntual o análisis de sensibilidad; un extremo plausible se conserva. Cualquier límite máximo o mínimo, incluida la saturación de valores extremos (*clipping*), necesita justificación por unidades, instrumento o desempeño validado **solo con pacientes de entrenamiento**. Si se ajustan umbrales estadísticos o transformaciones para el modelo, no usar pacientes de validación/prueba para calcularlos. Evaluar el impacto por clase y paciente para no eliminar desproporcionadamente etapas poco frecuentes.

El *binning* no corrige un error de medición: discretiza valores y pierde resolución. Solo sería una característica experimental si hay una razón interpretable o una mejora validada por pacientes. Primero determinar si el extremo es artefacto, variación legítima o un cambio de escala; después comparar, sin modificar el dataset base, conservarlo, transformarlo o limitarlo mediante una regla documentada.

## Pendientes de revisión — no implementados

1. Inspeccionar casos dirigidos en señal cruda: EDA del paciente 4 en los epochs 729–755 y 797, el paciente que concentra TEMP baja y epochs con BVP alto junto con aceleración. Verificar continuidad, escala, contacto, cobertura y cambios de etapa. La muestra exploratoria de 18 pacientes no basta para fijar reglas globales.
2. Clasificar los patrones observados como extremo plausible, artefacto confirmado, problema de escala o caso no resuelto. Registrar evidencia, pacientes, epochs y efecto potencial sobre cada etapa antes de definir un tratamiento.
3. Solo después de aprobar una regla concreta, corregir desde la fuente o invalidar la señal afectada cuando corresponda, conservar el dataset original y comparar cobertura, dimensiones y distribución por etapa/paciente antes y después. Repetir la auditoría sobre el conjunto completo antes de generalizar. No se fija aún ningún límite de clipping o binning.

**EDA en 2.6.4:** se documentó qué representa cada vista: rango entre pacientes, máximo, mayor salto entre muestras y acelerómetro simultáneo. No se corrigió el dataset: un valor elevado o un movimiento coincidente son hipótesis de revisión. Queda pendiente inspeccionar la forma cruda y el contexto de los tramos marcados en 3.3.1 antes de decidir si conservar EDA, corregir una escala confirmada o invalidar solo un tramo defectuoso.

La lista en memoria conserva `patient_id`, `epoch`, variable, criterio IQR y contexto; no se guarda un CSV nuevo. El mapa de calor puede complementar la revisión, pero no sustituye los controles de calidad ni convierte un valor extremo en error.
