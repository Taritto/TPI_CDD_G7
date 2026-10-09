---
status: accepted
date: 2026-09-28
---

# Mantener epochs de 30 segundos

## Implementación vigente

Implementado: epochs completos de 30 segundos y 3000 muestras a 100 Hz, con alineación por archivo o segmento verificable. Conservar tiempo relativo real; epoch identifica la ventana conservada y no sustituye el reloj.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Conservar ventanas completas, alineadas y no solapadas de 30 segundos: 3000 muestras a 100 Hz. La anotación de etapas tiene esa resolución. Dividir en ventanas de 15 segundos repetiría una etiqueta clínica y no duplicaría la información independiente.

La alineación se estima por archivo; si cambia dentro del registro, conservar únicamente segmentos verificables. El tiempo real del CSV permite representar los huecos de selección sin comprimirlos.

## Alineación y pureza

Los cambios entre etapas válidas se comparan por su posición módulo 3000. Una fase consistente identifica dónde deben comenzar las ventanas; no se presupone el mismo desplazamiento para todos los pacientes ni se fuerza uno si cambia dentro del archivo.

Un epoch conservado contiene una sola etapa válida en sus 3000 muestras, salvo la inferencia aislada definida en [ADR 0012](0012-etiquetas-missing-y-segmentos-alineados.md). Ventanas incompletas o ambiguas no reciben simplemente la etapa mayoritaria. La alternativa de 15 segundos se mantiene como experimento posible, no como forma de aumentar artificialmente el tamaño entregable.

## Consecuencias

No aumentar filas artificialmente para cumplir dimensiones. Otras duraciones o ventanas solapadas requerirían un experimento separado con su referencia temporal y validación por paciente.

## Fuentes

- [Descripción de DREAMT 2.2.0 en PhysioNet](https://physionet.org/content/dreamt/2.2.0/), que indica anotaciones de `Sleep_Stage` cada 30 segundos y señales PSG remuestreadas a 100 Hz.
