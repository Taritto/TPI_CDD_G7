---
status: accepted
date: 2026-09-28
---

# Conservar las apneas como contexto y excluir indicadores derivados del modelo principal

## Implementación vigente

Las anotaciones de apnea y los indicadores derivados de Sleep_Stage quedan fuera de los predictores candidatos. SAO2 e IBI tampoco integran el ETL de señales actual. La copia candidata ya construida es PSG + wearable. Para la entrega 3 se acordó wearable como escenario principal y PSG + wearable como comparación secundaria; los modelos todavía no están entrenados.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Las anotaciones `Obstructive_Apnea`, `Central_Apnea`, `Hypopnea` y `Multiple_Events` se conservan en los CSV originales como contexto, pero no se incorporan al ETL de señales ni al candidato principal. Son anotaciones clínicas, con distinta disponibilidad que una medición nueva. Las señales respiratorias originales sí pueden ser entradas.

Indicadores calculados a partir de `Sleep_Stage` (proporciones, latencias y transiciones) sirven para describir el registro, no para predecir esa misma etiqueta: incorporarlos produciría fuga de información. Comparar PSG + wearable y wearable solo requiere conjuntos de entrada y modelos propios, con las mismas particiones por paciente.

## Escenario acordado para modelar

Identificar la etapa del epoch actual; no anticipar la siguiente. Usar características wearable como `X` y la etapa anotada por PSG como `y`. Las señales PSG no son necesarias como entradas para aprender esa relación. Un modelo comparativo que las use como predictores debe entrenarse y evaluarse por separado; retirarlas durante inferencia no lo convierte en un modelo wearable.

## Variables incluidas y excluidas

`Sleep_Stage` es el objetivo; `patient_id` y `epoch` identifican observaciones y no entran en `X`. `tiempo_relativo_segundos` se conserva para trazabilidad; la candidata actual no lo usa como predictor, aunque se propone comparar un modelo con tiempo en la entrega 3.

La exclusión de anotaciones de apnea no elimina las señales medidas `SNORE`, `PTAF`, `FLOW`, `THORAX` y `ABDOMEN`: sus desviaciones estándar sí integran la candidata. `SAO2` e `IBI` permanecen en los CSV fuente, pero no en el ETL actual; reconsiderarlas exige revisar escala/calidad y reconstruir sus características con trazabilidad.

## Consecuencias

Conservar información en el archivo fuente no implica usarla como predictor. La selección final debe considerar calidad, disponibilidad y resultados de validación. Cualquier escenario con anotaciones clínicas adicionales debe identificarse explícitamente.

## Fuentes

- [DREAMT 2.2.0 - PhysioNet](https://physionet.org/content/dreamt/2.2.0/)
- [Resumen de actualizaciones de las reglas de puntuación de eventos respiratorios de AASM](https://aasm.org/wp-content/uploads/2017/11/Summary-of-Updates-in-v2.0-FINAL.pdf)
