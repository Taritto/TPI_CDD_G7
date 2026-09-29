# Distribuciones de predictores y desbalance de etapas

**Estado de implementación:** parcial. La sección 3.3.2 del notebook muestra histogramas globales y cajas por etapa para un conjunto acotado de predictores disponibles, además de cobertura y número de pacientes por variable y etapa. El recuento global de clases ya figura en 3.3 y las proporciones por paciente en 3.6. Se verificaron sintaxis y cálculos de cobertura con datos sintéticos; falta ejecutar e interpretar los gráficos con el dataset definitivo y confirmar unidades en fuentes. No se normalizó ningún predictor ni `Sleep_Stage`, y no se aplicó remuestreo o ponderación de clases. Quedan para la etapa de modelado los conteos por partición, métricas por clase y experimentos de balanceo ajustados solo en entrenamiento.

La distribución de una variable predictora y la frecuencia de las clases de `Sleep_Stage` son problemas distintos. La regresión logística no exige que los predictores tengan distribución normal. Una asimetría o una cola larga justifica revisar calidad, extremos o la conveniencia de una transformación; no obliga a recortar ni a «normalizar» la variable para volverla gaussiana. `Sleep_Stage` es categórica: no se normaliza como una variable numérica ni se fuerza a una distribución normal. Si N3 u otra etapa es poco frecuente, el problema es **desbalance de clases** y debe abordarse en entrenamiento y evaluación.

## Gráficos de distribución a implementar

Priorizar predictores con interpretación y potencial de aporte: resúmenes de HR, TEMP, EDA, BVP, aceleración, SAO2 si su calidad lo permite, y resúmenes PSG candidatos. Agregar variables marcadas por faltantes, extremos o mapas de asociación. Para cada candidata, usar una distribución global para conocer escala, ceros, colas y posibles valores inválidos, y una comparación por `Sleep_Stage` para observar superposición o diferencias. Mostrar unidades, cantidad de epochs y pacientes por clase, y cobertura de la señal. No producir gráficos de todas las columnas sin una pregunta exploratoria concreta; reservar inspecciones temporales o por paciente para patrones dudosos.

## Desbalance del objetivo

Mostrar recuentos y porcentajes de W, N1, N2, N3 y R tanto globalmente como por paciente y en cada partición de entrenamiento/validación/prueba. Una clase minoritaria puede quedar mal predicha aunque la exactitud global sea alta. Evaluar matriz de confusión, recuperación y precisión por etapa, y una métrica agregada que no oculte clases raras (por ejemplo, F1 macro). Comparar primero un modelo base sin intervención con alternativas como ponderación de clases; cualquier remuestreo se hará **solo dentro del entrenamiento** y respetando la separación por paciente. No duplicar epochs ni alterar la distribución de la prueba para simular más datos independientes. Elegir la estrategia por desempeño validado, no por una regla automática.

## Transformaciones

Escalado de predictores, transformaciones para asimetría y tratamiento de extremos son decisiones separadas del desbalance de `Sleep_Stage`. Si se usan, ajustar sus parámetros únicamente con pacientes de entrenamiento y aplicar luego a validación/prueba sin volver a calcularlos. Conservar los valores originales en el dataset base y documentar cada transformación experimental.
