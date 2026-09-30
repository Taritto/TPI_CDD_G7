# Plan ejecutable de revisión, transformación y selección de variables

**Objetivo:** pasar del dataset de epochs auditado a conjuntos de entrenamiento comparables, sin alterar los CSV originales ni confundir una marca exploratoria con un error confirmado. Este plan concreta las alternativas de [plan-transformacion-etl.md](plan-transformacion-etl.md) y la sección 3.8 del [notebook](../temporal_version_tp_cdd.ipynb). **Estado:** plan para decidir en equipo; las podas, el escalado y el entrenamiento aún no están aplicados.

**Dos alcances distintos:** la ejecución amplia informada por el equipo produjo 54.367 epochs de 73 pacientes incluidos; el cache local disponible contiene 13.165 epochs de 18 pacientes. Toda decisión de alcance global debe repetirse sobre el CSV amplio y registrar su versión. Si se incorporan más archivos, actualizar los recuentos antes de comparar.

## 1. Congelar y comprobar el dataset base

1. Ejecutar 3.1–3.2 con la cohorte elegida y anotar archivos auditados/incluidos/excluidos, epochs y clases. Guardar juntos `dataset_epochs_v1.csv`, `auditoria_epochs.csv`, `epochs_descartados.csv` y `manifest_etl_v1.json`. No forzar una reconstrucción si el manifiesto coincide.
2. Revisar en 3.2 la conciliación de S027/S048: filas crudas fuera de los tramos verificables, fragmentos continuos, ventanas completas y epochs conservados. **No desplazar etiquetas para recuperar más datos por conveniencia.** Confirmar las tres imputaciones aisladas de S089/S095/S096 y sus marcas.
3. Ejecutar 3.7 en la **misma cohorte**. Si una regla lógica falla, rastrear paciente/epoch/CSV crudo; corregir solo una causa demostrada. Si no hay violaciones, registrar ese resultado. Un valor finito no certifica calidad instrumental.
4. Revisar EDA S004/S057 y TEMP baja solo hasta poder decidir si existe un defecto concreto. Para EDA, contrastar mediana, p95/p99, duración de episodios elevados, continuidad y señales simultáneas; el gráfico de máximos de 2.6.4, aun con todos los archivos, no basta. Si la causa sigue incierta, **conservar con marca de revisión** y declararlo como limitación. No bloquear el resto por todos los puntos IQR.

**Salida de esta fase:** recuentos finales y lista de incidencias con decisión `conservar`, `invalidar señal/tramo comprobado` o `pendiente sin corrección`. Si se modifica una señal, recalcular sus resúmenes por epoch y comparar antes/después: filas, pacientes, faltantes, clases —especialmente N3/R— y auditoría. No eliminar un paciente por un máximo aislado.

## 2. Qué conservar, dejar fuera y comparar

«Dejar fuera» significa **no usar como predictor de la primera línea base**; no borrar del CSV de epochs.

| Grupo | Decisión inicial | Motivo / prueba posterior |
| :--- | :--- | :--- |
| `Sleep_Stage` | Conservar como objetivo `y`; nunca en `X`. | W, N1, N2, N3 y R son categorías, no una escala numérica de profundidad. |
| `patient_id`, `epoch` | Conservar en CSV. `patient_id` agrupa la partición; ninguno entra en `X` inicial. | Evitar que el modelo memorice personas; mantener secuencia y trazabilidad. |
| `tiempo_relativo_segundos` | Conservar; probar **solo** en el experimento de tiempo. | Refleja tiempo real transcurrido, incluso con huecos de S027/S048. No agregar simultáneamente `epoch` como segundo tiempo. |
| `TIMESTAMP` absoluto | Conservar para auditoría; fuera de `X` inicial. | Podría codificar el origen/horario del registro, no una señal fisiológica generalizable. |
| `porcentaje_pureza*`, `etiqueta_imputada`, `*_n_valid`, `*_missing_frac` | Conservar para calidad; fuera de `X` inicial. | Algunas columnas derivan del etiquetado o de disponibilidad del sensor; evaluar su uso solo si existirán al inferir y no introducen fuga. |
| Apneas anotadas | Fuera del objetivo principal. | Anotaciones clínicas, no señales fisiológicas continuas. |
| SAO2 e IBI | Fuera de la versión actual de características. | Pendientes de escala/calidad/disponibilidad; no reemplazar ceros ni convertir unidades a ciegas. |
| S097 y epochs con etiqueta inválida o tramo ambiguo | Mantener la exclusión supervisada ya documentada. | S097 presenta PSG constante; los tramos largos `Missing` y la alineación no verificable no admiten una etiqueta confiable. Conservar origen y auditoría. |
| `*_mean` y `*_median` alternativos; medias/medianas de señales PSG oscilatorias | Dejar fuera de la **primera línea base**, conservar en CSV. | Comparar luego media contra mediana de HR/TEMP/EDA y amplitud `*_std` contra nivel. Correlación alta o media cercana a cero no justifica borrado definitivo. |

**Línea base de señales sugerida:** wearable `HR_median`, `HR_std`, `TEMP_median`, `EDA_median`, `EDA_std`, `BVP_std`, `ACC_X_std`, `ACC_Y_std`, `ACC_Z_std`. En el escenario **PSG + wearable**, añadir inicialmente los `*_std` de los 17 canales PSG incluidos; en **wearable solo**, no usar ninguna columna PSG. Esta es una referencia para comparar, **no una selección final**. Revisar calidad de EDA antes de interpretar su aporte.

## 3. Qué transformar y resumir, y en qué orden

Trabajar siempre sobre copias. 3.5.4 ya crea ocho columnas candidatas sin eliminar las originales; no son el dataset final. Cambiar **una familia por experimento** y mantener idéntica partición de pacientes.

| Prueba | Variables | Condición para aplicarla | Comparar contra |
| :--- | :--- | :--- | :--- |
| `log1p(x)` | `BVP_std`, `EDA_median`, `ACC_X/Y/Z_std` | Valores no negativos; cola alta plausible tras la revisión de calidad. Comprime extremos, **no repara artefactos**. | Las mismas columnas originales sin transformar. |
| Escalado estándar o robusto | Variables continuas del modelo, sobre todo si se usa regresión logística regularizada. | Ajustar centro/escala **solo en pacientes de entrenamiento** y aplicar a validación/prueba. | Modelo sin escalado y, si hay colas fuertes, estándar frente a robusto. |
| `log1p(x/s)` o solo escalado | `EDA_std` y PSG `*_std` de magnitud diminuta. | `log1p(x)` directo casi no cambia esos valores; si se usa `s`, estimarlo solo en entrenamiento y documentar unidades. | Valor original/escalado; no imponer log por asimetría solamente. |
| Elegir nivel central | `HR_mean`/`HR_median`, `TEMP_mean`/`TEMP_median`, `EDA_mean`/`EDA_median`. | Usar mediana como referencia robusta; probar media o ambas si aportan información adicional en pacientes nuevos. | Mediana sola. |
| Máximo bilateral | `E1_std`/`E2_std` → `EOG_max_std`; `LAT_std`/`RAT_std` → `LEG_max_std`. | Probar contra canales separados; la media bilateral puede ocultar actividad unilateral. | Dos canales originales. |
| Norma ACC | `sqrt(ACC_X_std² + ACC_Y_std² + ACC_Z_std²)`. | Probar los **tres** ejes frente al resumen; no quitar Y ni combinar solo X+Z por intuición. No equivale a la desviación de la magnitud cruda. | X, Y y Z originales. |
| Reducción EEG | Pares C4-M1/F4-M1, T3-CZ/CZ-T4 y otros de Spearman alto. | Ablación por canal o familia; comprobar N3/R y estabilidad por paciente. No deducir causalidad de Spearman. | Todos los canales originales. |

**No aplicar ahora:** clipping/winsorización por IQR, binning general, imputación de señales o eliminación masiva de outliers. Un IQR casi nulo en PSG/EDA puede marcar valores legítimos. Si se confirma un defecto localizado, invalidar o corregir **esa señal y tramo** desde la fuente, con auditoría; `log1p` no sustituye esa corrección.

## 4. Evidencia que falta antes de elegir columnas

1. Reejecutar **3.4.3, 3.5.1, 3.5.2 y 3.5.3** con el CSV amplio: tiempo–etapa por paciente; consistencia de señales; redundancia global y dentro de pacientes; dominio y cola de `log1p`. La prueba temporal local de 18 pacientes mostró asociación descriptiva (AUC de rangos N3 0,310; R 0,633), **no utilidad predictiva demostrada** en los 73.
2. Revisar 3.4.1–3.4.2: Spearman entre predictores y separación por etapa. Los seis pares PSG con |Spearman| > 0,85 priorizan ablaciones, no borrados. La AUC univariada no mide beneficio conjunto del modelo.
3. Acordar con el equipo el escenario de uso: **PSG + wearable** o **wearable solo**. La primera opción dispone de canales usados para anotar sueño; la segunda responde si el wearable alcanza por sí mismo. No comparar modelos con distinta disponibilidad como si resolvieran la misma pregunta.

## 5. Comparación de modelos y criterio de decisión

Separar pacientes entre entrenamiento, validación y prueba, comprobando presencia de N3/R en cada partición (N3 apareció en 35 pacientes y R en 61 en la ejecución informada). Fijar la partición antes de elegir variables o transformaciones. Mantener validación y prueba con las frecuencias reales.

1. Con el **mismo algoritmo y partición**, comparar A: señales sin tiempo; B: solo `tiempo_relativo_segundos`; C: señales + tiempo. Esto decide si la asociación descriptiva del tiempo aporta generalización. `patient_id` no entra en `X`.
2. Sobre la mejor referencia de señales, comparar **una** transformación o reducción por vez con el original: `log1p`, escalado, media/mediana, ojos, piernas, ACC y EEG. Repetir en el escenario wearable solo si corresponde.
3. Evaluar matriz de confusión, F1 macro y precisión/recuperación/F1 de **cada** etapa, especialmente N3 y R; registrar también pacientes por etapa. No decidir por exactitud global sola ni por mejoras mínimas de una única partición.
4. Primero entrenar sin balanceo; luego comparar pesos de clase calculados solo con entrenamiento. Si sube la recuperación de N3/R pero crecen demasiado los falsos positivos, debatir el compromiso. No balancear el CSV ni fabricar epochs de validación/prueba.

**Regla de cierre para cada cambio:** registrar columnas antes/después, pacientes/epochs afectados, evidencia de calidad, métrica por etapa, ventaja, costo y decisión `aceptar`/`rechazar`/`pendiente`. Una columna se puede retirar de `X` si su ablación no empeora de manera relevante la evaluación en pacientes no vistos; permanece en el dataset base. Si las incidencias de calidad no se resuelven, conservarlas marcadas y hacer un análisis de sensibilidad con y sin los tramos afectados, sin ocultar la limitación.
