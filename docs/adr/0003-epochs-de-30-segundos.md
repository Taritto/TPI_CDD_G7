---
status: accepted
date: 2026-09-28
---

# Mantener epochs de 30 segundos

El dataset principal conservará ventanas completas, alineadas y no solapadas de 30 segundos (3000 muestras a 100 Hz). `Sleep_Stage` está anotada a esa resolución en DREAMT, por lo que dividir cada ventana en dos de 15 segundos asignaría la misma etiqueta clínica a ambas mitades sin obtener dos anotaciones independientes.

## Motivos

- Una ventana de 15 segundos contiene menos contexto temporal para caracterizar patrones cerebrales, oculares, musculares, cardíacos y respiratorios. Puede fragmentar eventos que se desarrollan dentro de los 30 segundos y volver menos estables algunas estadísticas. El efecto concreto depende de la característica y no se ha medido aún en este proyecto.
- Duplicar las filas de esta manera no duplica la cantidad de pacientes ni la cantidad de etiquetas clínicas independientes. Tratar ambas mitades como observaciones independientes puede llevar a interpretar de forma exagerada el tamaño efectivo de la muestra.
- Las ventanas solapadas repetirían además muestras de señal entre filas y complicarían la asignación de la etiqueta cuando abarcan dos epochs clínicos. No serán parte del dataset principal.

## Requisito de tamaño

La versión registrada del ETL contiene 49.062 epochs de 30 segundos y queda 938 filas por debajo del mínimo actualizado de 50.000. Se prevé incorporar aproximadamente entre 5 y 10 CSV adicionales de pacientes, como máximo, y procesarlos con las mismas reglas de alineación, calidad y exclusión. No se asumirá que todos los archivos aportan epochs utilizables: el cumplimiento del mínimo se verificará sobre el dataset consolidado final.

## Alcance y verificación futura

La opción de 15 segundos podrá estudiarse más adelante como experimento separado, conservando la referencia al epoch clínico de origen y comparando resultados sobre pacientes no vistos. No se usará únicamente para aumentar el conteo de filas exigido por la cátedra.

## Fuentes

- [Descripción de DREAMT 2.2.0 en PhysioNet](https://physionet.org/content/dreamt/2.2.0/), que indica anotaciones de `Sleep_Stage` cada 30 segundos y señales PSG remuestreadas a 100 Hz.
