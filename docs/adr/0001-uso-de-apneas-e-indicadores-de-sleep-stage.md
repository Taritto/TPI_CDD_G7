---
status: accepted
date: 2026-09-28
---

# Conservar las apneas como contexto y excluir indicadores derivados del modelo principal

El objetivo exclusivo del proyecto es predecir `Sleep_Stage` para cada epoch. Las anotaciones clínicas `Obstructive_Apnea`, `Central_Apnea`, `Hypopnea` y `Multiple_Events` se conservarán en el dataset consolidado para auditoría, análisis por paciente y estudios posteriores, pero quedarán marcadas como excluidas de los predictores del modelo principal. Esta separación evita confundir anotaciones clínicas posteriores con mediciones disponibles para una predicción nueva, sin perder información potencialmente útil.

## Evidencia y alcance

- En una exploración previa de 200.000 filas de cada uno de 12 CSV inspeccionados, las cuatro columnas de apnea presentaron únicamente `1` o ausencia de evento. Esta observación debe contrastarse con la cohorte objetivo. Son indicadores de eventos, no magnitudes continuas con valores extremos; por lo tanto, no corresponde aplicarles recorte estadístico ni estimar un máximo distinto de `1`.
- Un evento respiratorio puede cruzar límites entre epochs o coincidir parcialmente con un epoch rotulado como vigilia. La presencia de apnea no determina por sí sola una etapa y no se utilizará como regla para descartar REM.
- Las señales respiratorias originales (`PTAF`, `FLOW`, `THORAX`, `ABDOMEN` y `SNORE`) sí permanecerán como candidatas a predictores porque representan mediciones fisiológicas y no anotaciones clínicas derivadas.
- Esta decisión se aplica al modelo principal de clasificación de etapas. Podrá evaluarse aparte un modelo experimental que incluya las anotaciones de apnea, identificado explícitamente como un escenario con información clínica privilegiada y no comparable con inferencia wearable o en tiempo real.

## Indicadores derivados de `Sleep_Stage`

Los porcentajes por etapa, tiempo total dormido, latencia hasta REM, eficiencia del sueño, tiempo despierto, cantidad de transiciones y duración de episodios se calcularán únicamente después de disponer de una secuencia real o predicha de `Sleep_Stage`. No entrarán como predictores porque contienen información derivada del mismo objetivo y producirían fuga de información.

Estos indicadores se utilizarán para:

- describir la arquitectura del sueño de cada paciente;
- comparar secuencias reales y predichas a nivel de noche;
- evaluar si el modelo conserva proporciones, latencias y transiciones razonables;
- analizar el rendimiento en subgrupos, por ejemplo pacientes con distinta carga de apnea;
- detectar registros atípicos que necesiten inspección, sin eliminarlos automáticamente.

## Conjuntos de predictores previstos

Se entrenarán y compararán dos modelos independientes con la misma partición por paciente y las mismas métricas:

1. **PSG + wearable:** utilizará características derivadas de señales clínicas y del dispositivo wearable.
2. **Wearable-only:** utilizará únicamente características disponibles en el dispositivo wearable.

La familia matemática del algoritmo podrá ser la misma, pero cada alternativa tendrá su propio vector de entrada, escalado, regularización y parámetros aprendidos. No se entrenará un modelo completo para luego retirar columnas durante la inferencia.

## Consecuencias

- Conservar una columna en el dataset no implica utilizarla como predictor.
- El futuro diccionario de datos deberá clasificar cada columna por función: identificador, objetivo, predictor, control de calidad o contexto clínico excluido.
- La selección definitiva de características se realizará sobre los datos de entrenamiento y se validará por paciente.
- Las medias y medianas de señales oscilatorias quedan como candidatas a revisión, no a eliminación automática; esta decisión se documentará por separado cuando se analice la selección de variables.

## Fuentes

- [DREAMT 2.2.0 - PhysioNet](https://physionet.org/content/dreamt/2.2.0/)
- [Resumen de actualizaciones de las reglas de puntuación de eventos respiratorios de AASM](https://aasm.org/wp-content/uploads/2017/11/Summary-of-Updates-in-v2.0-FINAL.pdf)
