# Detección y tratamiento de valores anómalos

**Estado de implementación:** parcial. La sección 3.3.1 del notebook marca candidatos mediante 1,5 × IQR global en características disponibles de wearable y PSG; resume epochs y pacientes afectados, proporciones por etapa, cobertura y valores de epochs vecinos contiguos del mismo paciente. Si el IQR es nulo o hay pocos valores, informa que no puede aplicar el criterio. No cambia el dataset ni aplica recortes, imputaciones o exclusiones. Se verificó la sintaxis y la lógica con un ejemplo sintético; falta ejecutar e interpretar el reporte sobre el dataset completo. El objetivo es detectar posibles errores sin confundir rareza estadística con medición incorrecta.

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

## Cambio futuro a implementar

Completar el resumen de integridad y calidad por señal y revisar los gráficos globales de distribución junto con los candidatos generados. La lista en memoria contiene `patient_id`, `epoch`, variable, criterio IQR y contexto; no se guarda un CSV nuevo. Después de revisar resultados reales, acordar en otro paso límites concretos y tratamiento por variable. El mapa de calor puede complementar la revisión, pero no sustituye los controles anteriores ni convierte por sí solo un valor extremo en error.
