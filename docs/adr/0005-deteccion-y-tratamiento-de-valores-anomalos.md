---
status: accepted
date: 2026-09-29
---

# Detección y tratamiento de valores anómalos

## Implementación vigente

El IQR y las revisiones dirigidas están ejecutados en 3.3.1–3.3.3. Las marcas no se convierten en recortes o exclusiones automáticas. EDA elevada y otros casos instrumentales se conservan documentados hasta disponer de evidencia localizada.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Distinguir integridad del ETL, validez instrumental y extremos estadísticos. El IQR global es un criterio para marcar candidatos; las cajas por etapa aplican el criterio a grupos diferentes y sus extremos no necesariamente coinciden.

Antes de corregir, localizar el caso en paciente y tiempo, revisar cobertura, escala, continuidad y señales simultáneas. Un pico aislado y una elevación sostenida pueden requerir interpretaciones distintas. Movimiento simultáneo sugiere una hipótesis, no confirma un artefacto.

## Criterio y señales a revisar

La regla aplicada a cada característica es `IQR = Q3 − Q1`; marca valores menores que `Q1 − 1,5 × IQR` o mayores que `Q3 + 1,5 × IQR`. No son límites fisiológicos.

- `HR` e `IBI`: contrastar unidad, ceros, constancia y cobertura; HR y un intervalo entre latidos no son resúmenes idénticos. IBI no integra el ETL actual.
- `TEMP` y `EDA`: revisar mesetas, saltos, duración y diferencias por paciente; no exigir distribución normal.
- `BVP` y `ACC_X/Y/Z`: revisar dispersión alta, cambios bruscos y movimiento simultáneo sin asumir una causa.
- Señales PSG: diferenciar una amplitud media próxima a cero de una señal constante durante todo el registro. La exclusión de S097 responde a múltiples señales PSG constantes, no a una media pequeña.
- `SAO2`: confirmar escala antes de interpretar su rango; una codificación incierta no se corrige mediante IQR.

Registrar paciente, señal, intervalo temporal, evidencia y decisión. EDA elevada en S004/S057/S027 y temperatura baja requieren revisión localizada; una marca no basta para retirar pacientes.

## Tratamiento

Conservar extremos plausibles o no confirmados. Una corrección exige evidencia localizada, regla aprobada y trazabilidad. Comparar cobertura, etapas y pacientes antes/después. Clipping o binning no están aplicados; si se estudian, hacerlo en una copia y ajustar parámetros únicamente con entrenamiento.
