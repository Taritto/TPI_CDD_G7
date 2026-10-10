# Entrega 3 · Preparación del modelado

La [consigna disponible](<../transversal/Trabajo Práctico 2026.pdf>) pide seleccionar técnicas, definir parámetros, evaluar el modelo, recopilar resultados e interpretarlos. La secuencia siguiente es la propuesta del proyecto para cumplir ese alcance. Fuente: sección 4 del [notebook](../../temporal_version_tp_cdd.ipynb). La preparación y la copia candidata ya están implementadas; los pasos siguientes todavía no tienen resultados predictivos.

## Objetivo y evaluación acordados

Identificar `Sleep_Stage` (W, N1, N2, N3 o R/REM) del **epoch actual de 30 segundos** utilizando únicamente características del wearable. La etiqueta anotada mediante PSG es la respuesta de entrenamiento (`y`), no una entrada (`X`). No se anticipa la etapa siguiente.

El ETL base mantiene sus 128 columnas y supera el mínimo de 50 indicado por el docente según la aclaración del equipo. Ese requisito del dataset entregable no obliga a usar todas sus columnas como predictores. La copia ya exportada de 22 predictores corresponde a PSG + wearable: no se usará completa en el modelo principal.

Como punto de partida, la definición wearable del notebook contempla `HR_median`, `HR_std`, `TEMP_median`, `EDA_median`, `EDA_std`, `BVP_std`, `ACC_X_std`, `ACC_Y_std` y `ACC_Z_std`. La variante combinada sustituye BVP/EDA por log1p y los tres ejes por `ACC_axes_std_norm_log1p`. Se decidirá la variante mediante validación; identificadores, objetivo y columnas PSG no entran en el modelo principal. El tiempo queda fuera de la primera comparación.

Desarrollar y comparar con los 76 pacientes actualmente incluidos, separando **pacientes de entrenamiento y validación**. Los pacientes adicionales, que el equipo declara no utilizados en exploración ni decisiones anteriores, se reservan como prueba final: no incorporarlos al ajuste o selección. Verificar etiquetas, disponibilidad y calidad antes de la evaluación final con las mismas reglas del ETL.

La comparación PSG + wearable será secundaria, con un modelo independiente y las mismas particiones. Permite contrastar el aporte de señales adicionales; un modelo entrenado con ellas no puede simplemente retirarlas al predecir con wearable.

## Tareas y dependencias

Se puede trabajar por módulos, pero las entradas, particiones y evaluación deben quedar acordadas antes de comparar modelos. Asignar un responsable por tarea en esta tabla; el mismo integrante puede asumir varias. Los responsables todavía no se asignaron y las tareas no están ejecutadas.

| Tarea | Trabajo y resultado verificable | Depende de | Responsable |
| --- | --- | --- | --- |
| T1 · Datos y particiones | Validar el ETL de partida, definir columnas wearable y separar IDs de entrenamiento/validación. Registrar semilla, pacientes y cobertura de las cinco etapas; mantener pacientes nuevos fuera. | Acuerdos de esta página | Por asignar |
| T2 · Selección teórica | Revisar las presentaciones; justificar dos o tres candidatos y descarte por grupos. Definir una lista pequeña de configuraciones iniciales, todavía sin elegir ganador. | Objetivo wearable | Por asignar |
| T3 · Evaluación común | Preparar una función compartida de entrenamiento/evaluación y un clasificador trivial. Ajustar preprocesamiento solo con entrenamiento; obtener F1 macro, métricas por etapa, matriz de confusión y tiempos. | T1 y configuraciones de T2 | Por asignar |
| T4 · Modelos candidatos | Cada integrante implementa uno de los candidatos con las mismas particiones y función de evaluación. Entregar configuración, predicciones de validación, métricas y tiempos, sin tocar datos o particiones compartidos. | T1–T3 completos | Repartir un modelo por integrante |
| T5 · Ajustes y comparación | Consolidar resultados; comparar variantes originales/log1p/ACC y sin pesos/con pesos cuando el algoritmo lo admita. Ampliar ajustes solo si resuelven una pregunta concreta; elegir configuración con validación y costo. | Resultados de T4 | Por asignar |
| T6 · Errores y conclusiones | Revisar las cinco etapas, confusiones y variación por paciente. Distinguir calidad de datos, representación y algoritmo como explicaciones posibles; documentar evidencia y límites, sin atribuir causas clínicas no comprobadas. | Predicciones de T4; cerrar tras T5 | Por asignar |
| T7 · Comparación secundaria | Entrenar un modelo independiente PSG + wearable con la misma partición y evaluación. Presentar como contraste secundario, sin desplazar el objetivo wearable. | T3 y referencia wearable de T4 | Por asignar |
| T8 · Prueba final | Congelar modelo/configuración elegidos; procesar pacientes reservados con las mismas reglas y verificar sus IDs y cobertura. Evaluar una vez para el cierre, sin reajustar según esa prueba. Informar exclusiones y límites de cobertura. | T5 cerrado; T6 revisado | Por asignar |
| T9 · Informe | Integrar método, comparación, resultados y conclusiones. Cada responsable redacta su bloque cuando lo completa; el cierre incorpora la prueba final y distingue propuestas futuras. | Redacción durante T1–T7; cierre tras T8 | Por asignar |

**Orden práctico:** T1 y T2 pueden avanzar en paralelo → T3 → candidatos de T4 en paralelo → T5 y análisis T6 → T8 → cierre T9. T7 puede avanzar tras la primera referencia wearable; si limita el tiempo, se prioriza cerrar el escenario principal. Revisiones instrumentales puntuales se abren solo con evidencia; un cambio en entradas o particiones exige repetir las comparaciones afectadas.

## Outline de la sección de modelado del notebook

La numeración siguiente es una propuesta para reemplazar la sección 4 de próximos pasos cuando comience la implementación; aún no son celdas existentes.

- **4.1. Datos, objetivo y particiones por paciente** — T1.
- **4.2. Algoritmos y configuraciones iniciales** — T2.
- **4.3. Evaluación común y referencia trivial** — T3.
- **4.4. Modelos wearable** — T4; un bloque independiente por candidato.
- **4.5. Ajustes y comparación en validación** — T5.
- **4.6. Análisis de errores por etapa y paciente** — T6.
- **4.7. Comparación secundaria PSG + wearable** — T7.
- **4.8. Evaluación final en pacientes reservados** — T8.
- **4.9. Conclusiones y límites** — síntesis para T9.

## Acuerdos para integrar trabajo del equipo

T1 entrega columnas de entrada y listas de IDs que todos reutilizan; nadie vuelve a dividir los pacientes para su modelo. T3 fija la forma común de resultados: modelo, escenario, variante, configuración, F1 macro, exactitud, tiempo de entrenamiento/predicción y métricas por etapa. Las predicciones conservan `patient_id`, `epoch`, etiqueta real y predicha para analizar errores; los identificadores no entran al modelo.

Cada responsable modifica solo su bloque de notebook y documentación correspondiente. Si varios trabajan simultáneamente, usar ramas separadas y que un integrante integre los bloques compartidos; revisar los cambios antes de combinar archivos, sin sobrescribir el notebook completo. No hace falta duplicar todo el notebook en archivos «final» ni crear un historial paralelo a Git.

Los resultados se comparan con las mismas particiones y métricas. Evaluar precisión, recuperación y F1 de **W, N1, N2, N3 y REM**, además de F1 macro: atención a una minoritaria no sustituye evaluar las otras cuatro. La comparación final debe señalar cobertura y tradeoffs, no elegir solo por exactitud global.

## Cómo leer las métricas

Para cada etapa (por ejemplo, N3):

- **Precisión:** de los epochs que el modelo predijo como N3, qué proporción era realmente N3. Indica cuánto confiar en esa predicción.
- **Recuperación:** de todos los epochs que realmente eran N3, qué proporción detectó. Indica cuántos casos logra encontrar.
- **F1:** combina precisión y recuperación; será alto solo si ambas son altas. Se calcula como `2 × precisión × recuperación / (precisión + recuperación)` y va de 0 a 1; cuanto mayor, mejor.
- **F1 macro:** calcular F1 para W, N1, N2, N3 y REM y promediar los cinco con igual peso. Así una etapa frecuente como N2 no domina la medida. Acompañarlo con los resultados de cada etapa, porque el promedio puede ocultar diferencias.

Por ejemplo: si hay 100 epochs N3, el modelo marca 50 como N3 y acierta 40, su precisión es `40/50 = 0,80`, su recuperación `40/100 = 0,40` y su F1 aproximadamente `0,53`. Sus predicciones N3 suelen ser correctas, pero dejó sin detectar muchos N3. Estos números son ilustrativos, no resultados del proyecto.

**Exactitud global** es la proporción de todos los epochs clasificados correctamente; es distinta de la precisión por etapa. Si falta una etapa o el modelo nunca la predice, informar el caso y la convención usada para calcular las métricas, sin interpretarlo como buen desempeño.

## Estado y materiales

**Preparación, sin modelos ejecutados.** El alcance se contrastó con la consigna disponible; el equipo debe incorporar cualquier indicación adicional de la cátedra antes de fijar experimentos.

Punto de partida: [entrega 2](../entrega-02/README.md). Agregar aquí el informe y las figuras cuando existan; registrar escenario, cohorte, particiones, modelos y métricas efectivamente ejecutadas. No copiar la documentación de la entrega anterior.

## Límites a comprobar al evaluar

Media, mediana y desviación estándar resumen el epoch, pero no conservan completamente el orden de sus muestras: dos señales con el mismo resumen pueden tener ritmos o picos distintos. Si el modelo falla, revisar tanto algoritmo como calidad y representación. Solo con evidencia en entrenamiento/validación, considerar características adicionales wearable (por ejemplo, cambios dentro del epoch o componentes de frecuencia) mediante un experimento acotado, manteniendo el ETL base. Esto no implica que el modelo pierda precisión simplemente por pasar el tiempo ni se resuelve por sí solo con gráficos de control.

El desbalance puede favorecer etapas frecuentes y dificultar el reconocimiento de etapas con pocos ejemplos o pocos pacientes. La causa clínica o ambiental de esas frecuencias no se confirmó en este análisis: no atribuirlas automáticamente al entorno de PSG. El contexto de los participantes está en [contexto común](../transversal/contexto.md). Las estrategias y sus límites están en [ADR 0009](../adr/0009-distribuciones-y-desbalance-de-etapas.md).

## Propuesta futura condicionada a resultados

Si T6 muestra errores persistentes que justifiquen revisar la representación, comparar una ampliación acotada de características wearable (cambios dentro del epoch o componentes de frecuencia). No es una tarea obligatoria de esta primera comparación ni un defecto confirmado. Requiere revisar señales crudas y sus frecuencias originales/remuestreo, conservar el ETL base y decidir solo con entrenamiento/validación; véase [ADR 0007](../adr/0007-revision-y-seleccion-de-caracteristicas.md).
