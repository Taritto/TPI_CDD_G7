# Rangos válidos y recorte de valores extremos

**Estado de implementación:** parcial. La sección 3.7 del notebook informa violaciones lógicas de desviaciones estándar, recuentos de muestras válidas, fracciones y pureza, y comprueba la coherencia entre recuentos y fracciones de faltantes. Resume epochs y pacientes afectados, desglosa por etapa y conserva casos para rastrear en el CSV fuente. También describe ceros, cobertura y cuantiles de señales prioritarias sin convertirlos en topes. Se verificaron sintaxis y casos sintéticos con y sin violaciones. No se modifican datos ni se aplica clipping. Siguen pendientes la ejecución con registros completos, la confirmación de unidades/escala —especialmente SAO2—, la revisión de muestras crudas afectadas y cualquier límite o tratamiento específico.

**SAO2 en 2.6.2:** se aclaró que los recuentos dependen de la cohorte ejecutada y que valores fuera de 0–1 no autorizan una conversión automática: primero debe confirmarse si el registro usa fracción, porcentaje u otra codificación, y revisar tramos de ceros y saltos. Solo una conversión uniforme y verificada se corregiría desde la fuente; un tramo defectuoso afectaría a SAO2, no a `Sleep_Stage` ni al paciente completo. Hasta resolver la causa, SAO2 permanece fuera de los predictores principales.

Se separan tres conceptos: **rango válido por definición o escala**, **rango plausible según instrumento y contexto**, y **extremo estadístico**. Solo el primero permite una regla inequívoca una vez confirmadas unidades y transformaciones. Un extremo estadístico no es automáticamente error y no se recorta por defecto.

## Controles a implementar

- Verificar esquema, unidades y transformaciones desde el archivo fuente antes de definir umbrales. Contrastar valores crudos y resúmenes por epoch para localizar el origen del problema.
- Aplicar controles lógicos: desviaciones estándar y recuentos no negativos; proporciones de cobertura y pureza en [0, 1]; `SAO2` en [0, 1] **solo si se confirma que se expresa como fracción** (o en [0, 100] si se expresa como porcentaje). Una regla lógica no sustituye una validación de calidad clínica o instrumental.
- Para HR, IBI, TEMP, EDA y SAO2, inspeccionar ceros, valores extremos, señal plana, saltos bruscos, cobertura y continuidad con epochs vecinos antes de proponer rangos plausibles. No asignar todavía topes clínicos numéricos.
- Para BVP, ACC y señales PSG oscilatorias, no imponer máximos universales de amplitud: revisar unidades, saturación del sensor, artefactos, cambios de escala y contexto temporal. Una media cercana a cero puede ser normal para una señal oscilatoria.
- Informar por variable cuántas muestras, epochs y pacientes serían afectados por cada regla, y si la afectación cambia según `Sleep_Stage`. Mantener registro de casos candidatos, causa probable y decisión.

## Decisión sobre tratamiento

Los valores confirmados como inválidos se tratarán con una regla explícita y trazable, a decidir luego de revisar ejemplos; los extremos plausibles se conservarán inicialmente. Un recorte por percentiles (*clipping*) solo podrá probarse como transformación experimental para modelado, comparándolo con una versión sin recorte. Si se estiman límites a partir de los datos, calcularlos exclusivamente con pacientes de entrenamiento y aplicarlos sin reajuste a validación/prueba. Conservar el dataset fuente y el dataset base de epochs sin truncamiento automático.

La decisión anterior sobre apneas sigue vigente: las anotaciones de eventos no se usan como predictores del modelo principal y no reciben un «máximo» artificial para influir en `Sleep_Stage`.
