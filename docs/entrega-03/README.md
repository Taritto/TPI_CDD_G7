# Entrega 3 · Preparación del modelado

La [consigna disponible](<../transversal/Trabajo Práctico 2026.pdf>) pide seleccionar técnicas, definir parámetros, evaluar el modelo, recopilar resultados e interpretarlos. La secuencia siguiente es la propuesta del proyecto para cumplir ese alcance. Fuente: sección 4 del [notebook](../../temporal_version_tp_cdd.ipynb). La preparación y la copia candidata ya están implementadas; los pasos siguientes todavía no tienen resultados predictivos.

1. **Identificar la ejecución de partida.** Utilizar dataset, auditorías y manifiesto coherentes. La referencia guardada contiene 77 archivos, 76 pacientes y 56.850 epochs; una cohorte diferente necesita su propia ficha.
2. **Acordar escenario.** Comparar PSG + wearable y wearable solo según disponibilidad y objetivo. Las anotaciones de apnea y la etapa objetivo no se usan como entradas.
3. **Definir particiones por paciente.** Separar entrenamiento, validación y prueba; registrar IDs y semilla. Reservar la prueba final. Identificadores y número de epoch quedan fuera de X.
4. **Construir referencias y modelos iniciales.** Comparar clasificador trivial, regresión logística multiclase y modelo de árboles. Ajustar escalado y posibles pesos de clase únicamente con entrenamiento.
5. **Comparar representaciones.** Originales frente a log1p; resúmenes bilaterales y ACC frente a sus canales; ablaciones de EEG y experimentos con/sin tiempo. Usar las mismas particiones para comparar.
6. **Evaluar por etapa y paciente.** F1 macro, matriz de confusión, precisión y recuperación, con atención a N3/REM. No balancear validación o prueba ni elegir cambios consultando repetidamente la prueba final.
7. **Revisar casos instrumentales cuando haya evidencia.** Contrastar tramos crudos y su impacto antes de corregir señales o excluir más datos. Registrar decisión y comparación; conservar el ETL base.
8. **Documentar lo ejecutado.** Actualizar [decisiones comunes](../adr/README.md) cuando cambie una regla; guardar resultados, figuras y conclusiones de esta entrega en esta carpeta.

Los controles estructurales y las asociaciones exploratorias no sustituyen la evaluación en pacientes no vistos. El criterio para adoptar una transformación será su resultado en las comparaciones acordadas.

## Estado y materiales

**Preparación, sin modelos ejecutados.** El alcance se contrastó con la consigna disponible; el equipo debe incorporar cualquier indicación adicional de la cátedra antes de fijar experimentos.

Punto de partida: [entrega 2](../entrega-02/README.md). Agregar aquí el informe y las figuras cuando existan; registrar escenario, cohorte, particiones, modelos y métricas efectivamente ejecutadas. No copiar la documentación de la entrega anterior.
