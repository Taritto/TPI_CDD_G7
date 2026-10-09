---
status: accepted
date: 2026-09-29
---

# Revisión y selección de características

## Implementación vigente

Se construyó una copia candidata en 3.9 con 22 predictores, 3 columnas de trazabilidad y 1 objetivo. Se combinan ojos/piernas/ACC y se aplica log1p; el ETL base conserva sus 128 columnas. Selección final y mejora predictiva pendientes de modelado.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Conservar los resúmenes originales y la calidad en el ETL base; elegir una representación inicial en una copia. Medias o medianas próximas a cero en señales oscilatorias no prueban que la señal sea inútil: puede haber compensación de valores positivos y negativos.

La copia busca comprimir colas derechas y resumir canales relacionados. Combinar canales puede perder información de lado o eje; cambiar la escala no corrige fallos instrumentales. Las fórmulas y alternativas se detallan debajo para compararlas con los resúmenes originales.

## Transformaciones y alternativas

| Entradas | Columna candidata | Motivo y límite |
| --- | --- | --- |
| `BVP_std` | `BVP_std_log1p` | Comprimir valores altos sin recortarlos; comparar contra la escala original. |
| `EDA_median` | `EDA_median_log1p` | Reducir la dominancia visual y numérica de la cola derecha; no resolver incertidumbre instrumental. |
| `ACC_X_std`, `ACC_Y_std`, `ACC_Z_std` | `ACC_axes_std_norm_log1p` | `log1p(sqrt(ACC_X_std² + ACC_Y_std² + ACC_Z_std²))`; combinar dispersión, perdiendo información específica por eje. No es la std de la magnitud de ACC cruda. |
| `E1_std`, `E2_std` | `EOG_max_std` | Conservar la mayor dispersión ocular; perder lateralidad. |
| `LAT_std`, `RAT_std` | `LEG_max_std` | Conservar la mayor dispersión de piernas; perder lateralidad. |

La implementación exige entradas finitas y no negativas para estas transformaciones. `log1p` es una fórmula fija; no aprende parámetros de la cohorte. Escalado, selección u otras transformaciones que sí aprendan parámetros deben ajustarse solo en entrenamiento.

Alternativas previstas: características originales, transformaciones por separado y variante combinada. Los canales EEG `C4-M1_std`, `F4-M1_std`, `O2-M1_std`, `Fp1-O2_std`, `T3 - CZ_std` y `CZ - T4_std` permanecen: su correlación no demuestra que puedan retirarse sin afectar el modelo.

## Validación pendiente

Cobertura, variación y asociación descriptiva orientan candidatos. Su aporte se comprueba mediante modelos y ablaciones, con preprocesamiento ajustado solo en entrenamiento. No seleccionar por un número arbitrario de predictores ni borrar alternativas del ETL base.

## Criterio para decidir después

En 3.5.1 se contrastan, por paciente, medianas de una etapa frente al resto para `HR_median`, `TEMP_median`, `EDA_median`, `BVP_std`, `ACC_X_std`, `C4-M1_std`, `E1_std` y `FLOW_std`. Se requieren al menos cinco epochs válidos en cada grupo; casos sin cobertura suficiente no se convierten en cero.

Antes de retirar o conservar definitivamente una característica, registrar significado, unidad, calidad/cobertura, patrón entre pacientes, redundancia y resultado de ablación (modelo con y sin ella). Mantener iguales las particiones y observar métricas por clase. Una superposición visual, un coeficiente alto o pasar los controles de construcción no sustituye esa comparación.
