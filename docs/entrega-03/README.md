# Entrega 3 · Preparación del modelado

La [consigna disponible](<../transversal/Trabajo Práctico 2026.pdf>) pide seleccionar técnicas, definir parámetros, evaluar el modelo, recopilar resultados e interpretarlos. La secuencia siguiente es la propuesta del proyecto para cumplir ese alcance. Fuente: sección 4 del [notebook](../../temporal_version_tp_cdd.ipynb). La preparación y la copia candidata ya están implementadas; los pasos siguientes todavía no tienen resultados predictivos.

## Objetivo y evaluación acordados

Identificar `Sleep_Stage` (W, N1, N2, N3 o R/REM) del **epoch actual de 30 segundos** utilizando características de **wearable + PSG como escenario principal**. El escenario **solo wearable** será la comparación secundaria. La etiqueta anotada mediante PSG es la respuesta de entrenamiento (`y`), no una entrada (`X`); las características de las señales PSG sí pueden entrar en el escenario principal. No se anticipa la etapa siguiente.

El ETL base mantiene sus 128 columnas. El equipo prioriza wearable + PSG para atender la indicación docente de trabajar con varias entradas. La copia ya exportada de **22 predictores (7 wearable y 15 PSG)** es el punto de partida principal. El mínimo de 50 columnas del dataset no equivale a 50 predictores: si el docente exige ese mínimo para las entradas del modelo, esta candidata aún no lo cumple y habrá que aclarar el requisito antes de fijar las características.

Para la comparación secundaria, la definición wearable del notebook contempla `HR_median`, `HR_std`, `TEMP_median`, `EDA_median`, `EDA_std`, `BVP_std`, `ACC_X_std`, `ACC_Y_std` y `ACC_Z_std`. La variante combinada sustituye BVP/EDA por log1p y los tres ejes por `ACC_axes_std_norm_log1p`. Se decidirá la variante mediante validación; identificadores y objetivo no entran en ningún modelo; las columnas PSG quedan fuera del secundario solo wearable. El tiempo queda fuera de la primera comparación.

Desarrollar y comparar con los 76 pacientes actualmente incluidos mediante **validación cruzada con `StratifiedGroupKFold`, inicialmente con cinco particiones**, usando `patient_id` como grupo y `Sleep_Stage` para estratificar. Cada paciente permanece completo en entrenamiento o validación dentro de cada ronda; todos los modelos y ambos escenarios reutilizan las mismas particiones. La estrategia está elegida, pero aún no implementada ni comprobada sobre estos datos. Los pacientes adicionales, que el equipo declara no utilizados en exploración ni decisiones anteriores, se reservan como prueba final: no incorporarlos al ajuste o selección. Verificar etiquetas, disponibilidad y calidad antes de la evaluación final con las mismas reglas del ETL.

La estratificación intenta conservar proporciones similares de etapas, sin balancear clases ni garantizar proporciones idénticas. No requiere que cada paciente tenga las cinco etapas. Antes de entrenar, comprobar que no se comparten pacientes y registrar epochs y pacientes con presencia de cada etapa en entrenamiento y validación de cada ronda. Si la cobertura resulta insuficiente, reconsiderar el número de particiones (por ejemplo, tres), sin elegir la división por el desempeño obtenido.

La comparación solo wearable tendrá un modelo independiente, las mismas particiones y métricas que el principal. Informar F1 macro, exactitud y precisión/recuperación por etapa de ambos escenarios para contrastar el aporte de PSG. Un modelo entrenado con PSG no puede simplemente retirarla al predecir con wearable.

## Modelos y estrategia inicial

Comparar un **clasificador trivial** que prediga la etapa más frecuente del entrenamiento, **regresión logística multiclase**, **Random Forest** y **XGBoost**. La logística permite medir qué aportan relaciones lineales; los dos ensamblados de árboles son candidatos fuertes para capturar relaciones no lineales e interacciones. Ninguno queda elegido como ganador antes de evaluarlo. T2 debe justificar la selección con las presentaciones y señalar XGBoost como complemento externo al desarrollo de los algoritmos de la cátedra; véase su [fundamento oficial](https://xgboost.readthedocs.io/en/stable/tutorials/model.html).

La métrica principal será **F1 macro**, acompañada de precisión, recuperación y F1 por etapa, exactitud y tiempos. La primera comparación usa las características ya preparadas y contrasta entrenamiento sin pesos y con pesos, según el [ADR 0009](../adr/0009-distribuciones-y-desbalance-de-etapas.md). SMOTE queda como experimento condicionado al diagnóstico en T5, no como paso inicial obligatorio. Comparar configuraciones con las mismas particiones, entradas por escenario y un presupuesto de ajustes comparable; dedicar más esfuerzo a candidatos prometedores según F1 macro, resultados por etapa y costo.

## Tareas y dependencias

Se puede trabajar por módulos, pero las entradas, particiones y evaluación deben quedar acordadas antes de comparar modelos. Asignar un responsable por tarea en esta tabla; el mismo integrante puede asumir varias. Los responsables todavía no se asignaron y las tareas no están ejecutadas.

| Tarea | Trabajo y resultado verificable | Depende de | Responsable |
| --- | --- | --- | --- |
| T1 · Datos y particiones | Validar el ETL de partida, definir columnas de wearable + PSG y del secundario solo wearable, y generar/guardar las particiones de StratifiedGroupKFold. Registrar número de particiones, configuración de mezcla y semilla cuando corresponda, IDs y cobertura de las cinco etapas por ronda; mantener pacientes nuevos fuera. | Acuerdos de esta página | Por asignar |
| T2 · Selección teórica | Revisar las presentaciones; justificar logística multiclase, Random Forest y XGBoost, además de la referencia trivial, y el descarte por grupos. Definir una lista pequeña de configuraciones iniciales, todavía sin elegir ganador. | Objetivo wearable + PSG | Por asignar |
| T3 · Evaluación común | Preparar una función compartida de entrenamiento/evaluación y un clasificador trivial. Entrenar desde cero en cada ronda y ajustar preprocesamiento, selección y posibles pesos solo con su entrenamiento; guardar etiquetas predichas y probabilidades de las cinco etapas por epoch de validación, métricas y tiempos por ronda. Resumir F1 macro con promedio y desviación estándar. | T1 y configuraciones de T2 | Por asignar |
| T4 · Modelos candidatos | Cada integrante implementa uno de los candidatos del escenario principal wearable + PSG con las mismas particiones y función de evaluación. Entregar configuración, predicciones y probabilidades de validación, métricas y tiempos, sin tocar datos o particiones compartidos. | T1–T3 completos | Repartir un modelo por integrante |
| T5 · Ajustes y comparación | Consolidar resultados; comparar variantes originales/log1p/ACC y sin pesos/con pesos cuando el algoritmo lo admita. Dedicar ajustes acotados a candidatos prometedores; considerar SMOTE o características adicionales solo si T6 lo justifica. Elegir configuración con validación y costo. | Resultados de T4 | Por asignar |
| T6 · Errores y conclusiones | Construir matriz acumulada, curvas Precision-Recall y reportes por etapa y paciente con las predicciones de validación de T4/T5. Distinguir calidad de datos, representación y algoritmo como explicaciones posibles; documentar evidencia y límites, sin atribuir causas clínicas no comprobadas. | Predicciones de T4; cerrar tras T5 | Por asignar |
| T7 · Comparación secundaria | Entrenar un modelo independiente solo wearable con la misma partición y evaluación. Comparar sus métricas con el principal wearable + PSG. | T3 y referencia wearable + PSG de T4 | Por asignar |
| T8 · Prueba final | Congelar configuraciones elegidas por escenario y reentrenar con todos los pacientes de desarrollo, reajustando allí el preprocesamiento y los posibles pesos. Procesar los reservados con las mismas reglas, verificar IDs/cobertura y evaluar sin reajustes posteriores; generar matriz y métricas finales. Informar exclusiones y límites de cobertura. | T5/T6 cerrados y T7 si se realiza | Por asignar |
| T9 · Informe | Integrar método, comparación, resultados y conclusiones. Cada responsable redacta su bloque cuando lo completa; el cierre incorpora la prueba final y distingue propuestas futuras. | Redacción durante T1–T7; cierre tras T8 | Por asignar |

**Orden práctico:** T1 y T2 pueden avanzar en paralelo → T3 → candidatos de T4 en paralelo → T5 y análisis T6 → T7 → T8 → cierre T9. T7 puede avanzar tras la primera referencia wearable + PSG; si limita el tiempo, se prioriza cerrar el escenario principal. Revisiones instrumentales puntuales se abren solo con evidencia; un cambio en entradas o particiones exige repetir las comparaciones afectadas.

## Outline de la sección de modelado del notebook

La numeración siguiente es una propuesta para reemplazar la sección 4 de próximos pasos cuando comience la implementación; aún no son celdas existentes.

- **4.1. Datos, objetivo y particiones por paciente** — T1.
- **4.2. Algoritmos y configuraciones iniciales** — T2.
- **4.3. Evaluación común y referencia trivial** — T3.
- **4.4. Modelos wearable + PSG** — T4; un bloque independiente por candidato.
- **4.5. Ajustes y comparación en validación** — T5.
- **4.6. Análisis de errores por etapa y paciente** — T6.
- **4.7. Comparación secundaria solo wearable** — T7.
- **4.8. Evaluación final en pacientes reservados** — T8.
- **4.9. Conclusiones y límites** — síntesis para T9.

## Acuerdos para integrar trabajo del equipo

T1 entrega columnas de entrada y listas de IDs por partición que todos reutilizan; nadie vuelve a dividir los pacientes para su modelo. T3 fija la forma común de resultados: modelo, escenario, variante, configuración, ronda, F1 macro, exactitud, tiempo de entrenamiento/predicción y métricas por etapa. Resumir F1 macro mediante promedio y desviación estándar entre rondas, conservando los resultados individuales. Las predicciones conservan modelo/configuración, escenario, variante, ronda, `patient_id`, `epoch`, etiqueta real, predicha y probabilidades de W, N1, N2, N3 y R, con orden de clases explícito, para analizar errores; los identificadores no entran al modelo.

Cada responsable modifica solo su bloque de notebook y documentación correspondiente. Si varios trabajan simultáneamente, usar ramas separadas y que un integrante integre los bloques compartidos; revisar los cambios antes de combinar archivos, sin sobrescribir el notebook completo. No hace falta duplicar todo el notebook en archivos «final» ni crear un historial paralelo a Git.

Los resultados se comparan con las mismas particiones y métricas. Evaluar precisión, recuperación y F1 de **W, N1, N2, N3 y REM**, además de F1 macro: atención a una minoritaria no sustituye evaluar las otras cuatro. La comparación final debe señalar cobertura y tradeoffs, no elegir solo por exactitud global. Los resultados de validación cruzada se usan para seleccionar y ajustar; no sustituyen la evaluación independiente en los pacientes reservados.

## Diagnóstico global por modelo

Para cada configuración y escenario, reunir las predicciones **out-of-fold**: cada epoch de desarrollo se predice exactamente una vez, durante la ronda en que su paciente queda en validación. El modelo que genera esa predicción no entrenó con ese paciente. Conservar separados los resultados de configuraciones distintas; el detalle de columnas está en los acuerdos de integración anteriores.

- **Matriz de confusión acumulada:** cruzar etapa real (filas) y predicha (columnas), con el mismo orden de las cinco etapas. Mostrar cantidades y porcentajes normalizados por fila; la diagonal son aciertos y el resto muestra con qué etapa se confunde cada una. Si no hay ejemplos de una etapa, señalar que no es evaluable.
- **Curvas Precision-Recall por etapa:** usar las probabilidades de validación de cada etapa frente al resto. Muestran cómo cambian precisión y recuperación al variar el umbral; las etiquetas predichas solas no alcanzan para construirlas.
- **Reporte de clasificación:** precisión, recuperación, F1 y cantidad de ejemplos reales de cada etapa. Evaluar las cinco; N3/REM merecen atención sin omitir W, N1 y N2.
- **Resultados por fold y paciente:** conservar F1 macro por ronda, promedio y desviación estándar, y revisar diferencias individuales con su cobertura de etapas. El agregado por epochs da más peso a registros largos; no equivale al promedio de pacientes. La desviación estándar describe variación entre rondas, no prueba superioridad estadística.

La matriz acumulada no conserva el orden temporal. Si se investigan falsas transiciones, comparar también secuencias reales y predichas por paciente y segmento continuo. Esta revisión es adicional al diagnóstico por epoch. Los gráficos acumulados sirven para diagnóstico y selección en validación; la prueba final genera sus propias métricas y matriz por separado.

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

Si la validación indica que los resúmenes wearable limitan el modelo, comparar primero más características ya disponibles en el ETL (medias, medianas y desviaciones estándar). Si no basta, considerar una ampliación acotada desde señales crudas, como cambios internos o características de frecuencia.

Si se prueban retardos o ventanas móviles, calcularlos por paciente y segmento continuo, ordenados por tiempo y usando solo señales disponibles hasta el epoch actual. Reiniciar el contexto ante huecos; no usar etapas reales anteriores como entradas. Los cálculos deterministas pueden prepararse antes de los folds con esas condiciones; cualquier transformación aprendida se ajusta dentro del entrenamiento de cada ronda. Es una opción futura, no un error confirmado ni una tarea inicial; conservar el ETL base y evaluar sin consultar la prueba final. Véase [ADR 0007](../adr/0007-revision-y-seleccion-de-caracteristicas.md).
