---
status: accepted
date: 2026-09-28
---

# Generar un único dataset consolidado de epochs

**Estado de implementación:** parcial, con ejecución local verificada. La sección 3.1 acepta una cantidad variable de archivos y produce un único CSV de epochs ordenado por `patient_id` y `epoch`, más auditoría y detalle de descartes. Valida claves, etiquetas, orden y conservación de filas y ventanas; no genera datasets completos por paciente ni `pacientes_pendientes.csv`. La ejecución guardada del usuario con 18 CSV locales produjo 13.165 epochs y 126 columnas, sin nulos ni descartes. Los tres archivos se localizaron en `B:\kaggle\working\etl_v1` porque la ruta de salida estaba fijada para Kaggle; se copiaron y verificaron en `etl_v1/` del proyecto. El notebook ahora usa `/kaggle/working/etl_v1` solo en Kaggle y `etl_v1/` del directorio de trabajo en local, e imprime la ruta absoluta. Los CSV crudos no se tocaron. Falta incorporar suficientes pacientes para verificar el mínimo de 50.000 filas y revisar los resultados científicos. Parquet sigue recomendado, pero no implementado.

El ETL generará un único dataset principal con todos los pacientes, ordenado de forma estable por `patient_id` y `epoch`. Esta salida simplifica el modelado y evita mantener copias completas por paciente, pero conserva la identidad y la secuencia mediante la clave compuesta `(patient_id, epoch)`.

## Salidas

El resultado principal será:

- `dataset_epochs_v1.parquet`, como formato recomendado para conservar tipos y reducir tamaño;
- `dataset_epochs_v1.csv`, cuando sea necesario entregar o inspeccionar un formato portable.

No se generarán datasets completos separados por paciente. Los CSV crudos de origen permanecerán intactos y separados.

Tampoco se generará `pacientes_pendientes.csv`. Las exclusiones o incidencias de pacientes deberán quedar documentadas en el notebook y en la auditoría del ETL, sin sumar otro archivo específico.

## Orden y clave

El dataset se ordenará por:

1. `patient_id` ascendente;
2. `epoch` ascendente dentro de cada paciente.

La posición física de una fila no será su identidad. La combinación `(patient_id, epoch)` deberá ser única y permitirá reconstruir la secuencia aunque el dataset sea filtrado u ordenado posteriormente.

El archivo persistido no se mezclará aleatoriamente. Cualquier aleatorización ocurrirá durante el modelado, después de separar los conjuntos por `patient_id`, para evitar que epochs de un mismo paciente aparezcan simultáneamente en entrenamiento y evaluación.

## Auditoría de epochs

Se conservará `auditoria_epochs.csv` como salida auxiliar pequeña y separada del dataset de modelado. Su propósito es demostrar cómo cada archivo crudo contribuyó al resultado consolidado y permitir explicar diferencias entre filas originales, ventanas posibles y epochs finalmente utilizados.

Como mínimo registrará por paciente:

- archivo y `patient_id`;
- cantidad de filas originales;
- estado de continuidad temporal;
- desplazamiento utilizado para alinear las ventanas;
- cantidad de epochs completos detectados;
- filas de los fragmentos inicial y final;
- epochs descartados por etiquetas inválidas o por no cumplir el criterio vigente;
- epochs conservados en el dataset final.

Este archivo no será utilizado como entrada del modelo. Se mantiene por trazabilidad, control del requisito de cantidad de filas y capacidad de reproducir el ETL.

## Consecuencias

- El entrenamiento utilizará una única fuente de datos procesados.
- El orden temporal se preservará dentro de cada paciente.
- La separación entre entrenamiento, validación y prueba deberá realizarse por paciente, no por filas aleatorias.
- Los errores o exclusiones deberán poder explicarse mediante la auditoría, aunque no exista un archivo independiente de pacientes pendientes.
- El dataset consolidado deberá validarse comprobando unicidad de `(patient_id, epoch)`, orden, dominio de `Sleep_Stage`, cantidad de pacientes y cantidad total de epochs.
