# Contexto común del proyecto

Objetivo: identificar la etapa del epoch actual de 30 segundos (W, N1, N2, N3 o REM) usando señales del wearable de DREAMT, con la etapa anotada por PSG como referencia. PSG + wearable se estudiará como comparación secundaria con un modelo independiente. La etapa objetivo es categórica. Cada entrega documenta sus propios resultados; las [decisiones comunes](../adr/README.md) mantienen las reglas que siguen aplicándose.

## Fuentes y materiales

- [DREAMT en PhysioNet](https://www.physionet.org/content/dreamt/2.2.0/): descripción y acceso al dataset. El enlace no confirma por sí solo la versión de los CSV de Kaggle.
- [CSV utilizados en Kaggle](https://www.kaggle.com/datasets/diegopetitto/dreamt-data).
- [Notebook utilizado en Kaggle](https://www.kaggle.com/code/lautarocastillo/tpi-cdd-g7).
- [Consigna del trabajo práctico](<Trabajo Práctico 2026.pdf>): alcance de las cuatro entregas. El año del nombre del archivo fue actualizado por el equipo; el texto del PDF no indica año.

## Trabajo en equipo

El [notebook principal](../../temporal_version_tp_cdd.ipynb) contiene código y salidas. Una ejecución local con menos archivos no reemplaza la corrida completa de Kaggle. Dataset, auditorías y manifiesto deben corresponder a una misma ejecución. CSV crudos y salidas regenerables de `etl_v1/` permanecen fuera de Git.

El ETL base y la copia candidata representan los mismos epochs: no concatenarlos como observaciones nuevas. Conservar la versión guardada de Kaggle y el commit correspondiente al cerrar cada entrega. Git conserva la historia; evitar notebooks «final2» y copias completas de documentación.

## Contexto de los participantes y generalización

La [descripción oficial de DREAMT, sección Methods](https://physionet.org/content/dreamt/2.2.0/#methods) indica reclutamiento en Duke Sleep Disorder Lab, un protocolo orientado a detectar/monitorizar apnea y participantes con apnea obstructiva del sueño. Es una población de estudio clínico; el desempeño obtenido no se extrapola automáticamente a personas sanas durmiendo en casa.

El `participant_info.csv` compartido por el equipo contiene 100 participantes y columnas `SID`, `AGE`, `GENDER`, `BMI`, `OAHI`, `AHI`, `Mean_SaO2`, `Arousal Index`, `MEDICAL_HISTORY` y `Sleep_Disorders`. Se comprobaron registros con antecedentes de apnea y trastornos respiratorios. Este archivo describe la colección completa, no prueba que las mismas proporciones correspondan a los 76 pacientes del ETL. No se copia a Git como parte de esta actualización; su acceso se obtiene con el dataset de referencia.

El contexto clínico y el entorno de medición son factores plausibles para discutir la representatividad, pero no demuestran la causa de la baja proporción de N3 observada. No afirmar que pacientes concretos no alcanzaron etapas por los cables, el laboratorio o la apnea sin un análisis específico.

Estos metadatos no se agregan como entradas del modelo wearable. En especial, `AHI`, `OAHI` y `Arousal Index` se obtienen del estudio clínico y no deben introducirse inadvertidamente como información disponible del wearable. Si se evalúan subgrupos, unir `SID` con `patient_id` validando identidad y cobertura, usar inicialmente solo pacientes de desarrollo y señalar tamaños por grupo. No examinar resultados por subgrupo de la prueba reservada para decidir ajustes.
