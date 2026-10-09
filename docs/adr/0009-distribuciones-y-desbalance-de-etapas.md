---
status: accepted
date: 2026-09-29
---

# Distribuciones de predictores y desbalance de etapas

## Implementación vigente

Análisis descriptivo ejecutado en 3.3. El ETL mantiene las frecuencias observadas, sin balanceo. Los recuentos y la cobertura vigentes se consultan en [entrega 2](../entrega-02/README.md); posibles pesos de clase se compararán solo en entrenamiento.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Preservar frecuencias originales de `Sleep_Stage` en el ETL. La distribución de predictores y el desbalance de clases son problemas distintos: una cola larga no obliga a recortar, y una etiqueta categórica no se normaliza para volverla gaussiana.

La exactitud global puede favorecer a la clase mayoritaria. Por eso el modelado debe informar métricas por etapa y F1 macro, junto con matriz de confusión. Las cifras de la ejecución de referencia están en [entrega 2](../entrega-02/README.md).

## Alternativas futuras

Comparar primero una referencia sin balanceo y luego posibles pesos de clase solo en entrenamiento. Remuestreo requiere justificación: repetir epochs no genera pacientes nuevos; submuestrear pierde información. Mantener las proporciones originales de validación y prueba y revisar el intercambio entre recuperación y falsos positivos.

## Evaluación y alternativas de balanceo

F1 macro promedia el F1 de cada etapa con el mismo peso. Complementarlo con precisión, recuperación y matriz de confusión: una mejora en recuperación de N3 puede venir acompañada de más falsos positivos.

Ponderar clases cambia el costo de sus errores, no sus etiquetas; sobremuestrear repite ejemplos y submuestrear retira parte del entrenamiento. Ninguna opción se aplica al ETL base ni queda elegida por el desbalance solo. Definir particiones por paciente antes de calcular pesos o remuestrear y contrastar cada alternativa contra la referencia sin balanceo.
