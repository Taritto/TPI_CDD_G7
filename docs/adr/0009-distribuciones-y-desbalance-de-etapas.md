---
status: accepted
date: 2026-09-29
---

# Distribuciones de predictores y desbalance de etapas

## Implementación vigente

Análisis descriptivo ejecutado en 3.3. El ETL mantiene las frecuencias observadas, sin balanceo. Los recuentos y la cobertura vigentes se consultan en [entrega 2](../entrega-02/README.md). El modelado compara pesos por observación y amplía las pruebas a SMOTE sobre el mejor candidato de cada escenario; resultados y estado en [entrega 3](../entrega-03/README.md).

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Preservar frecuencias originales de `Sleep_Stage` en el ETL. La distribución de predictores y el desbalance de clases son problemas distintos: una cola larga no obliga a recortar, y una etiqueta categórica no se normaliza para volverla gaussiana.

La exactitud global puede favorecer a la clase mayoritaria. Por eso el modelado debe informar métricas por etapa y F1 macro, junto con matriz de confusión. Las cifras de la ejecución de referencia están en [entrega 2](../entrega-02/README.md).

## Alternativas de entrenamiento

Comparar primero una referencia sin balanceo y luego posibles pesos de clase solo en entrenamiento. Remuestreo requiere justificación: repetir epochs no genera pacientes nuevos; submuestrear pierde información. Mantener las proporciones originales de validación y prueba y revisar el intercambio entre recuperación y falsos positivos.

## Evaluación y alternativas de balanceo

F1 combina precisión (cuántas predicciones de una etapa son correctas) y recuperación (cuántos casos reales de esa etapa se detectan). F1 macro promedia el F1 de cada etapa con el mismo peso; véase la [lectura de métricas](../entrega-03/README.md#qué-mirar). Informar precisión, recuperación y F1 de W, N1, N2, N3 y REM, junto con matriz de confusión. No limitar la evaluación a N3/REM: mejorar recuperación de una etapa puede aumentar sus falsos positivos o perjudicar otras.

Ponderar clases cambia el costo de sus errores, no sus etiquetas; el sobremuestreo aleatorio repite ejemplos, SMOTE interpola ejemplos sintéticos y submuestrear retira parte del entrenamiento. Ninguna opción se aplica al ETL base ni queda elegida por el desbalance solo. Definir particiones por paciente antes de calcular pesos o remuestrear y contrastar cada alternativa contra la referencia sin balanceo.

## Riesgo y estrategia inicial acordada

Una clase con pocos epochs o presente en pocos pacientes puede ofrecer menos ejemplos para aprender y una evaluación menos estable. Esto puede reducir su recuperación, pero no demuestra de antemano que el modelo fallará. La menor frecuencia observada no permite atribuir una causa clínica ni concluir que el entorno hospitalario impidió alcanzar una etapa.

Comparar inicialmente entrenamiento sin pesos frente a ponderación por clase en los algoritmos que la admitan. Como primera configuración a evaluar, `class_weight="balanced"` asigna pesos inversos a la frecuencia de **las etiquetas de entrenamiento**, no a la cohorte completa. Aumenta el costo de equivocarse en etapas menos frecuentes; no crea pacientes ni patrones nuevos y puede aumentar falsos positivos. Es una configuración candidata, no una mejora garantizada. Fuente complementaria: [documentación oficial de scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html).

Para XGBoost multiclase, comparar pesos por observación mediante `sample_weight`, calculados a partir de las etiquetas de entrenamiento de cada ronda; `class_weight` no es una opción compartida por todos los algoritmos. Referencia complementaria: [API oficial de XGBoost](https://xgboost.readthedocs.io/en/stable/python/python_api.html).

Comprobar etapas y pacientes disponibles en cada partición, mantener validación/prueba con su distribución original y comparar F1 macro, recuperación y precisión por etapa. No sobremuestrear inicialmente: primero evaluar si los pesos aportan mejora estable. Si faltan patrones de una etapa, ponderarla no sustituye mejorar características o incorporar datos representativos en un ciclo posterior, sin reutilizar la prueba final para entrenar la versión que se está evaluando.

**SMOTE como opción condicionada en T5:** si persiste baja recuperación de N3 u otra etapa tras comparar pesos, probarlo en un candidato prometedor. Genera características sintéticas interpolando ejemplos de la misma clase; por las diferencias entre pacientes puede producir combinaciones poco representativas y no aporta sujetos nuevos. Aplicarlo únicamente a predictores del entrenamiento de cada fold, sin identificadores, tras ajustar allí la escala usada para buscar vecinos; registrar proporción de sobremuestreo y número de vecinos. Mantener validación y prueba originales. Conservarlo solo si aporta mejora consistente en validación, revisando F1 macro y precisión/recuperación de todas las etapas. Referencias complementarias: [funcionamiento de SMOTE](https://imbalanced-learn.org/stable/over_sampling.html) y [prevención de fuga al remuestrear](https://imbalanced-learn.org/stable/common_pitfalls.html).

La baja detección observada de N1 justifica ejecutar esa comparación controlada. Usar vecinos 3/5 y cantidades objetivo por clase del 50/100 % de la mayoritaria, sin reducir clases. Comparar sin pesos, con pesos y control escalado sin remuestreo; SMOTE no combina ponderación adicional ni historia temporal en esta ronda. Medir entrenamiento sobre observaciones reales, no sobre los ejemplos sintéticos. Una mejora de recuperación no basta si cae F1 macro o aumentan excesivamente los falsos positivos.

El contexto clínico y las limitaciones de generalización se documentan en [contexto común](../transversal/contexto.md). Es evidencia sobre la población de origen, no una causa demostrada del desbalance de la cohorte procesada.
