# Contexto común del proyecto

Objetivo: clasificar etapas del sueño W, N1, N2, N3 y REM mediante señales de DREAMT. La etapa objetivo es categórica. Cada entrega documenta sus propios resultados; las [decisiones comunes](../adr/README.md) mantienen las reglas que siguen aplicándose.

## Fuentes y materiales

- [DREAMT en PhysioNet](https://www.physionet.org/content/dreamt/2.2.0/): descripción y acceso al dataset. El enlace no confirma por sí solo la versión de los CSV de Kaggle.
- [CSV utilizados en Kaggle](https://www.kaggle.com/datasets/diegopetitto/dreamt-data).
- [Consigna del trabajo práctico](<Trabajo Práctico 2026.pdf>): alcance de las cuatro entregas. El año del nombre del archivo fue actualizado por el equipo; el texto del PDF no indica año.

## Trabajo en equipo

El [notebook principal](../../temporal_version_tp_cdd.ipynb) contiene código y salidas. Una ejecución local con menos archivos no reemplaza la corrida completa de Kaggle. Dataset, auditorías y manifiesto deben corresponder a una misma ejecución. CSV crudos y salidas regenerables de `etl_v1/` permanecen fuera de Git.

El ETL base y la copia candidata representan los mismos epochs: no concatenarlos como observaciones nuevas. Conservar la versión guardada de Kaggle y el commit correspondiente al cerrar cada entrega. Git conserva la historia; evitar notebooks «final2» y copias completas de documentación.
