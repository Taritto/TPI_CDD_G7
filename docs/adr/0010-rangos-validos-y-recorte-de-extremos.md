---
status: accepted
date: 2026-09-29
---

# Rangos válidos y recorte de valores extremos

## Implementación vigente

Controles lógicos ejecutados en 3.7, sin aplicar clipping ni límites fisiológicos arbitrarios. La ausencia de violaciones lógicas no certifica el instrumento; escala de SAO2 y otros casos requieren evidencia adicional.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Distinguir rango válido por definición, rango plausible instrumental y extremo estadístico. Confirmar unidades y escala antes de imponer límites; no convertir SAO2 automáticamente a porcentaje ni limitar EDA por magnitud aislada.

Los controles lógicos del ETL revisan desviaciones y recuentos no negativos, fracciones entre 0 y 1 y coherencia entre muestras válidas y faltantes. No establecen por sí solos plausibilidad clínica ni máximos universales para señales PSG.

## Reglas comprobadas y alcance

- `*_std`: valores definidos finitos y no negativos.
- `*_n_valid`: recuentos enteros entre 0 y 3000.
- `*_missing_frac`, `porcentaje_pureza` y `porcentaje_pureza_original`: fracciones entre 0 y 1.
- Por señal: `missing_frac = 1 − n_valid / 3000`, con tolerancia numérica `1e-4`.
- `Sleep_Stage`: una de W, N1, N2, N3 o R; comprobar claves, duración y conciliación de proporciones.

El control distingue valores ausentes de infracciones sobre valores definidos; un resultado sin infracciones no prueba ausencia de todos los faltantes. HR, IBI, TEMP, EDA y SAO2 requieren contexto instrumental para definir rangos plausibles. Para BVP, ACC y PSG no se adoptan topes universales de amplitud.

## Tratamiento

No hay clipping global. Una señal confirmada como inválida requiere una regla trazable, conservando fuente y ETL base. Si se prueban límites aprendidos de datos para modelar, estimarlos solo en entrenamiento y evaluar impacto por etapa y paciente.
