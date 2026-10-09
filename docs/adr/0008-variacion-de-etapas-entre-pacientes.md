---
status: accepted
date: 2026-09-29
---

# Variación de etapas entre pacientes

## Implementación vigente

Variación entre pacientes y relación temporal ejecutadas en 3.6 y 3.4.2. Usar tiempo_relativo_segundos para tiempo transcurrido. La separación por paciente para entrenamiento y evaluación es una decisión para implementar en el modelado, aún no ejecutado.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Describir proporciones de etapas y duración por paciente. Una etapa no observada se registra como tal, no como ausencia fisiológica; puede depender de duración, fragmentos conservados o anotación. No excluir una persona por REM temprano o por no tener N3 observado.

Para analizar tiempo, usar `tiempo_relativo_segundos`; el índice `epoch` no es un reloj. Las comparaciones temporales deben indicar origen del tiempo y cobertura. Los indicadores derivados de las etiquetas no son entradas para predecir la misma etiqueta.

## Indicadores temporales y cobertura

`duracion_valida_min` suma la duración de los epochs conservados; `tramo_observado_min` mide desde el primero hasta el último, incluyendo posibles huecos. `huecos_temporales` y `transiciones_contiguas` se calculan con tiempo real: no contar una transición a través de un tramo ausente.

`latencia_rem_desde_primer_sueno_min` cuenta desde el primer epoch de sueño conservado hasta el primer REM observado. No equivale necesariamente a latencia clínica desde el inicio real del sueño. Si REM no aparece, queda sin valor y con `estado_rem = no observado`; `latencia_rem_con_huecos` advierte si hay huecos entre ambos puntos.

En la vista temporal de 3.4.2 el origen es el inicio del CSV. AUC > 0,5 indica aparición generalmente posterior al resto de etapas, y < 0,5, anterior. Las proporciones por bloques de 30 minutos distinguen peso por epoch e igual peso por paciente; informar cobertura antes de interpretar los últimos bloques.

## Consecuencias

Separar entrenamiento, validación y prueba por paciente para evitar compartir señales de la misma persona. Revisar cobertura de clases por partición y evaluar variación entre pacientes, sin ajustar la prueba final según el desempeño.
