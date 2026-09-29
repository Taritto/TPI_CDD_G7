# Modelado posterior a la entrega de ETL

**Estado de implementación:** diferido. El cierre de la sección ETL del notebook explicita que todavía no se entrenó ni evaluó ningún algoritmo. En la entrega actual se documentan los pasos de modelado, pero no se aplicarán salvo que, una vez completado y verificado el ETL, el equipo decida ampliar el alcance. No presentar resultados de modelos como si ya existieran.

El objetivo futuro será predecir `Sleep_Stage` (W, N1, N2, N3, R). REM no se tratará como un escalón en una escala simple de profundidad; por ello, la regresión logística inicial será **multiclase**, no ordinal. No se presupone que sea el peor modelo: se usa como referencia interpretable.

## Comparación futura propuesta

1. Referencia trivial que predice la clase mayoritaria, para establecer un mínimo verificable.
2. Regresión logística multiclase regularizada como modelo base.
3. Random Forest como primera alternativa no lineal. Considerar gradient boosting solo si aporta a una pregunta o mejora verificable y hay tiempo para evaluarlo correctamente.

Comparar los mismos conjuntos de predictores definidos previamente (PSG + wearable y solo wearable) con particiones por `patient_id`, sin compartir pacientes entre entrenamiento, validación y prueba. La imputación, el escalado, la selección, los eventuales límites estadísticos y cualquier ponderación/remuestreo se ajustarán solo dentro de entrenamiento. Evaluar con matriz de confusión, métricas por etapa y F1 macro, prestando atención a clases minoritarias; no elegir un ganador solo por exactitud global. Verificar cobertura de etapas en las particiones y mantener la prueba final sin ajustes guiados por sus resultados. Ningún modelo o técnica de balanceo queda aprobado como ganador antes de medirlo.

## Alcance de la entrega ETL

La prioridad actual es un dataset de epochs reproducible y auditable: fuentes y unidades, alineación a 30 segundos, integración de pacientes, etiquetas, calidad/cobertura, controles de anomalías, EDA justificable y dataset final con dimensiones verificadas. El informe puede cerrar con la pregunta predictiva, los conjuntos de señales previstos, la prevención de fuga entre pacientes, métricas y algoritmos candidatos como **pasos siguientes**, claramente separados de lo implementado. No desviar esfuerzo del ETL hacia entrenamiento prematuro mientras falte validar extracción, transformación y carga.
