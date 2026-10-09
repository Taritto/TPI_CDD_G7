---
status: accepted
date: 2026-09-29
---

# Mapas de asociación y variables correlacionadas

## Implementación vigente

Mapas y tablas ejecutados en 3.4: relaciones generales de Spearman, cruce wearable–PSG, asociación por etapa (3.4.1) y temporal (3.4.2). No se eliminan canales por alta correlación. La selección definitiva depende de comparaciones predictivas por paciente.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Usar Spearman para relaciones monotónicas entre características; el triángulo evita repetir pares simétricos. El mapa cruzado wearable–PSG compara modalidades. Excluir identificadores, objetivo y sus derivados de estos mapas de predictores.

La asociación por etapa usa AUC de rangos uno contra el resto y se muestra como `2 × AUC − 1`. Un signo positivo indica valores generalmente mayores en esa etapa; negativo, menores. No es rendimiento de un clasificador. La asociación temporal usa tiempo real y se estudia por paciente.

## Variables y condiciones de comparación

La vista original compara nueve características wearable (`BVP_std`, `HR_median`, `HR_std`, `EDA_median`, `EDA_std`, `TEMP_median`, `ACC_X_std`, `ACC_Y_std`, `ACC_Z_std`) con las desviaciones estándar de 17 señales PSG. Este conjunto exploratorio de 26 características es distinto de las 26 columnas del archivo candidato, que incluyen objetivo y trazabilidad.

Spearman requiere al menos 30 epochs con datos comunes por par; constancia o cobertura insuficiente pueden impedir calcularlo. `|Spearman| > 0,85` es un criterio para listar pares a revisar, no para retirarlos.

No correlacionar con `Sleep_Stage_num`: numerar W/N1/N2/N3/R impondría un orden arbitrario. En la AUC por etapa se compara una característica en un epoch de esa etapa frente a otro del resto; los empates aportan medio peso. El signo del mapa indica dirección, no bondad ni error. Comparar con estabilidad dentro de pacientes para no confundir diferencias entre personas con diferencias entre etapas.

## Consecuencias

Alta correlación no autoriza eliminar una característica. Comparar ablaciones con las mismas particiones por paciente; revisar estabilidad, cobertura y utilidad incremental. SAO2 e IBI no están en el conjunto actual, por lo que correlaciones históricas de esas variables no son resultados vigentes.
