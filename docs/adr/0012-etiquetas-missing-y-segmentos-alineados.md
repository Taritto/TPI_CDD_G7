---
status: accepted
date: 2026-09-30
---

# Tratar etiquetas Missing y rescatar solo segmentos alineados

## Implementación vigente

Implementado y reflejado en 3.2: S027/S048 conservan 532/677 epochs de segmentos verificables. Se infirieron tres Missing completos aislados (S089/S095/S096) con vecinos puros iguales dentro de un tramo continuo. La intervención conserva etiqueta_imputada y porcentaje_pureza_original.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Inferir una etiqueta solo para un epoch completo de 3000 muestras con Missing o etiqueta nula, entre dos epochs originales completos, puros y de la misma etapa válida dentro del mismo fragmento continuo. La intervención ocurre en memoria; conserva `etiqueta_imputada` y `porcentaje_pureza_original`. No inferir tramos largos, vecinos distintos ni etiquetas parciales ambiguas.

Para S027/S048 recuperar únicamente segmentos con continuidad a 100 Hz y al menos dos cambios válidos que compartan fase módulo 3000. Ningún epoch cruza saltos temporales o cambios de fase. Registrar segmentos recuperados y filas excluidas en auditoría; no mover etiquetas arbitrariamente para recuperar más ventanas.

## Condiciones y trazabilidad

`Missing` y etiqueta nula se cuentan muestra a muestra; la inferencia exige que las 3000 muestras del epoch pertenezcan a ese caso. Los dos vecinos se comprueban con las etiquetas originales, evitando encadenar imputaciones para rellenar tramos largos.

Si los vecinos difieren o falta uno verificable, la ventana se descarta con su motivo en `epochs_descartados.csv`. Filas iniciales/finales incompletas, segmentos no alineados o un paciente excluido pueden quedar fuera antes de generar esas ventanas: un archivo de descartes vacío no significa que se conservaron todas las filas originales. `auditoria_epochs.csv` registra esa diferencia.

No usar mayoría de etiquetas ni desplazar todo el archivo para resolver una inconsistencia. Una nueva anotación especializada o un método de pseudoetiquetado requeriría un experimento separado; sus inferencias no se tomarían como verdad clínica de la prueba.

## Consecuencias

La regla reduce la intervención, pero presupone continuidad de etapa entre los vecinos: una etiqueta inferida no equivale a una anotación clínica confirmada. Se conserva distinguible de la anotación original. Los fragmentos no verificables permanecen fuera del dataset supervisado. La política es una decisión del proyecto, no una receta obligatoria de la fuente ni una confirmación de la causa de cada Missing.
