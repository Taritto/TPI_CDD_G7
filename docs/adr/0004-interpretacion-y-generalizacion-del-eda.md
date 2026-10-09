---
status: accepted
date: 2026-09-29
---

# Interpretación y generalización de los gráficos exploratorios

## Implementación vigente

Ejecutado en la cohorte de 77 archivos auditados y 76 pacientes incluidos. Las asociaciones y las figuras son descriptivas; no demuestran causalidad, calidad instrumental ni rendimiento de un clasificador. La muestra cruda individual es ilustrativa.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

El EDA describe los datos y orienta preguntas de calidad. Una muestra individual ilustra el formato, pero no representa toda la cohorte; las conclusiones globales requieren la auditoría y el dataset consolidado.

Las cajas muestran mediana, mitad central y dispersión de características por epoch. Sus extremos no certifican errores de sensor. Comparaciones por paciente ayudan a reconocer diferencias individuales que una vista agrupada puede ocultar.

## Características y lectura de las vistas

Las cajas de 3.3.2 comparan `HR_median`, `TEMP_median`, `EDA_median`, `BVP_std`, `ACC_X_std` y `C4-M1_std`. HR/TEMP/EDA resumen un nivel; `*_std` describe dispersión dentro del epoch. `BVP_std` no equivale a variabilidad de frecuencia cardíaca ni `ECG_std` a frecuencia cardíaca.

Ocultar puntos extremos modifica la figura, no los datos. En una vista agrupada, pacientes con más epochs pesan más; la comparación dentro de pacientes ayuda a comprobar si la dirección del patrón se repite. Movimiento en `ACC_X/Y/Z` puede acompañar valores extremos de BVP, pero no confirma artefactos ni vuelve intercambiables las señales.

El mapa EDA usa la mediana de `EDA_median` en bloques de cinco minutos y `log1p` para visualizar. Un bloque blanco no aporta epochs representados; puede ser fin del registro o un tramo no conservado. No demuestra por sí solo pérdida de EDA cruda.

## Límites

No atribuir causas clínicas a magnitudes, correlaciones o etapas no observadas. La capacidad de clasificar se mide entrenando y evaluando en pacientes separados, no mediante diferencias visuales.
