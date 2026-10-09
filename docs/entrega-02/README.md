# Entrega 2 · Auditoría, análisis y ETL

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb), sus salidas guardadas de 3.2 y 3.9. La entrega de preparación está cerrada; no hay modelos entrenados ni métricas predictivas.

## Ejecución de referencia

| Resultado | Cantidad |
| --- | ---: |
| Archivos auditados | 77 |
| Pacientes incluidos | 76 |
| Registros procesados completos / parciales / excluidos | 74 / 2 / 1 |
| Epochs de 30 segundos | 56.850 |
| Columnas del ETL base | 128 |
| Etiquetas inferidas | 3 |
| Columnas candidatas / predictores | 26 / 22 |

S027 y S048 se incluyen parcialmente con 532 y 677 epochs; S097 se excluye por señales PSG constantes. Las tres etiquetas inferidas corresponden a S089, S095 y S096. Los 633 casos de auditoría son marcas de revisión, no errores confirmados.

## Límites documentados

EDA elevada en S004/S057/S027, temperatura baja y escala/calidad de SAO2/IBI requieren evidencia localizada antes de corregirse. SAO2, IBI y anotaciones de apnea quedan fuera del candidato inicial. La recuperación parcial de S027/S048 está implementada; la incertidumbre instrumental no equivale a un ETL pendiente de construir.

N2 representa 51,96 % y N3 3,87 % de los epochs. N3 se observa en 36 pacientes y REM en 64; esto no demuestra ausencia fisiológica en el resto.

## Continuación

Para la entrega 3, acordar escenario, separar entrenamiento/validación/prueba por paciente y comparar modelos y representaciones. Evaluar por etapa y conservar la prueba final para la evaluación acordada. El [plan de continuidad](../entrega-03/README.md) detalla la secuencia propuesta, todavía no ejecutada.

## Material de esta entrega

- [Guía del notebook](guia-resumen-notebook.md): explicación siguiendo sus secciones.
- [Informe en Google Docs](https://docs.google.com/document/d/1UVepRrhdAaUAjK-SjD71dNQbgSHqWKQ_hOUdYKQ1Cn8/edit): documento compartido y revisado con el equipo.
- [Resumen y guía en PDF](Resumen-gu%C3%ADa-entrega2.pdf): material local de apoyo, separado del informe compartido.

Las reglas comunes están en [decisiones del proyecto](../adr/README.md). Esta página registra la ejecución de referencia de la entrega 2; los resultados posteriores se agregan en su propia entrega.

## Problema y unidad de análisis

Clasificación supervisada multiclase de `Sleep_Stage`: W, N1, N2, N3 y R (REM). La fila cruda corresponde a una muestra a 100 Hz; la fila procesada es un epoch de 30 segundos, con 3000 muestras. Las cinco etiquetas se tratan como categorías, sin imponer una escala ordinal.

## Auditoría y reglas de construcción

Se auditan los 77 archivos por bloques: lectura, continuidad temporal, etiquetas, alineación y señales. Cada archivo tiene su propia fase de alineación, inferida mediante cambios entre etapas válidas módulo 3000. En 75 archivos es consistente; S027/S048 se recuperan por segmentos verificables, sin forzar una fase única.

Las marcas de revisión no confirman errores de sensor. S097 se excluye por señales PSG constantes. EDA elevada, temperatura baja y escala de SAO2 permanecen documentadas; no se aplican recortes generales. Un Missing completo aislado se infiere solo entre dos epochs vecinos puros de la misma etapa dentro de un segmento continuo. El CSV original permanece intacto.

## Resultado del ETL

La ficha de referencia resume inclusión y dimensiones. Las etiquetas inferidas se identifican con `etiqueta_imputada`; `porcentaje_pureza_original` conserva el estado anterior a la intervención.

Las 128 columnas son 24 señales (7 wearable y 17 PSG) × 5 resúmenes (`mean`, `median`, `std`, `n_valid`, `missing_frac`) más 8 columnas: `patient_id`, `epoch`, `TIMESTAMP`, `tiempo_relativo_segundos`, `Sleep_Stage`, `porcentaje_pureza`, `porcentaje_pureza_original`, `etiqueta_imputada`. No todas son predictores.

La salida de descartes contiene cero epochs en esta ejecución; la exclusión de S097 y las filas fuera de segmentos alineados se registran en la auditoría y no deben interpretarse como datos íntegramente conservados.

## Reproducción y trazabilidad

Guardar juntos dataset, auditoría, descartes y manifiesto de una misma ejecución. Las claves y los controles de exportación verifican integridad; la caché se reutiliza únicamente si coinciden fuentes y reglas. En Kaggle, una salida guardada debe adjuntarse a una sesión posterior para poder reutilizarla: la copia local de `/kaggle/working` no garantiza persistencia entre sesiones.
