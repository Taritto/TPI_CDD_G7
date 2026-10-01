---
status: accepted
date: 2026-09-30
---

# Tratar etiquetas Missing y rescatar solo segmentos alineados

El dataset supervisado admite una única imputación de `Sleep_Stage`: un epoch completo de 3000 muestras con etiqueta `Missing` o nula, flanqueado dentro del mismo tramo continuo por dos epochs completos, puros y de la misma etapa válida. La etiqueta se completa solo en memoria; el CSV fuente permanece intacto. El resultado conserva `etiqueta_imputada=True` y `porcentaje_pureza_original=0` para distinguir inferencia de anotación PSG. Ambas columnas son metadatos de auditoría, no predictores.

Si los vecinos son distintos, no se elige uno arbitrariamente. El epoch se registra con motivo específico en `epochs_descartados.csv`, y las señales originales siguen disponibles. Alternativas para una decisión posterior: recodificación por especialista a partir de PSG, uso sin etiqueta en un enfoque semisupervisado o pseudoetiquetado experimental entrenado sin el paciente evaluado. Una pseudoetiqueta nunca se utilizará como verdad de prueba. Tramos prolongados, ventanas parcialmente `Missing` o casos sin dos vecinos verificables quedan fuera del dataset supervisado sin rellenar. Los tramos pueden estar asociados a reconfiguración de la PSG, como documenta DREAMT, o a problemas de medición/anotación que requieren comprobación individual.

Para S027 y S048 se permite recuperar únicamente segmentos con timestamps consecutivos a 100 Hz y al menos dos cambios entre etapas válidas que compartan fase respecto de 3000 muestras. Ningún epoch cruza un salto temporal o un cambio de fase. Se guardan en `auditoria_epochs.csv` los intervalos de filas recuperados y las filas aún excluidas; si no hay segmento verificable, el paciente permanece excluido. No se corrigen desplazamientos moviendo etiquetas para que encajen.

**Estado de implementación:** lógica incorporada en 3.1 y explicada/resumida en 3.2 del notebook. Prueba sintética aprobada para imputación aislada, vecinos distintos, tramo largo, salto de tiempo, cambio de fase y ausencia de segmento recuperable. Falta ejecutar y validar específicamente S027, S048 y los registros con `Missing` cuando estén presentes en la cohorte objetivo; una ejecución que no incluya esos archivos no demuestra su tratamiento.

**Fuente externa:** [DREAMT 2.2.0, PhysioNet](https://physionet.org/content/dreamt/2.2.0/) documenta etiquetas cada 30 segundos y tramos `Missing` asociados a reconfiguración de la PSG. Las reglas de tratamiento son decisiones del proyecto, no una indicación de la fuente ni un requisito de la cátedra.
