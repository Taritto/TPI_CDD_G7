# Guía del notebook vigente

Sigue el notebook principal y sus salidas de referencia: 77 archivos, 76 pacientes y 56.850 epochs. La entrega 2 comprende preparación y análisis; la sección 4 plantea el modelado pendiente. Las explicaciones de versiones anteriores pueden consultarse en el historial de Git; la numeración de esta guía sigue el notebook actual.

# 0. Objetivo y alcance

Clasificación multiclase de etapas del sueño. Definir el objetivo y distinguir muestras crudas de epochs.

## 0.1. Configuración

Preparar librerías y opciones de ejecución; no transforma datos.

## 0.2. Claves y exportación

Definir claves y exportaciones: una clave repetida, como `(patient_id, epoch)`, indica que la misma observación aparece más de una vez. Valores de señales iguales en epochs distintos no son por sí solos duplicados.

# 1. Entrada y reglas temporales

Detectar archivos y establecer las reglas temporales; la muestra individual no determina la cohorte.

# 2. EDA de los registros crudos

Revisar registros originales antes de construir el dataset.

### Variables originales

Distinguir señales wearable, PSG, etiquetas y eventos; confirmar unidades cuando corresponda.

## 2.1. Ficha de entrada

Comprobar estructura, tipos, tiempos y formato del registro.

## 2.2. Auditoría global

Revisar todos los archivos por bloques y registrar marcas de calidad sin corregir automáticamente.

### 2.2.1. Alineación y etiquetas

Inferir la fase por archivo; recuperar segmentos verificables de S027/S048 y tratar Missing bajo la regla de vecinos iguales.

### 2.2.2. SAO2: escala pendiente

SAO2 tiene escala incierta, especialmente S027 cerca de 12. No convertir arbitrariamente ni usarla en el candidato.

### 2.2.3. Señales constantes

Una señal constante requiere contexto; S097 se excluye por múltiples canales PSG constantes.

### 2.2.4. EDA elevada: casos para revisión

Inspeccionar EDA elevada y señales simultáneas; magnitud alta no confirma defecto ni causa clínica.

# 3. Dataset de epochs y transformación candidata

Pasar de muestras a una tabla trazable por epoch y analizarla antes del modelado.

## 3.1. Construcción o carga del ETL

Construir epochs completos de 3000 muestras o cargar una caché validada; no cruzar saltos temporales ni fases incompatibles.

## 3.2. Resultado y decisiones del ETL

Conciliar archivos, pacientes y epochs: 74 completos, 2 parciales y 1 excluido; 3 etiquetas inferidas.

## 3.3. Etapas y cobertura

Contar etapas y cobertura por paciente. N2 domina y N3 es minoritaria; no balancear el ETL.

### 3.3.1. Candidatos atípicos: marcas, no descartes

IQR es Q3 menos Q1. Los valores fuera de Q1−1,5 IQR y Q3+1,5 IQR son marcas exploratorias, no descartes.

### 3.3.2. Distribuciones de predictores

Cajas: línea central = mediana, caja = mitad central de valores. Bigotes hasta 1,5 IQR; ocultar puntos en la figura no los elimina. Histogramas muestran colas derechas.

#### Señales crudas: un paciente

Usar un paciente para contextualizar señales crudas; no generalizar esa vista a toda la cohorte.

### 3.3.3. EDA por paciente y tiempo

Comparar EDA por paciente y tiempo en bloques de 5 minutos. Colores representan log1p del resumen; blancos = sin epochs representados en ese bloque.

## 3.4. Relaciones entre predictores

Spearman mide asociación monotónica. La matriz triangular evita repetir pares; correlación alta orienta comparaciones, no elimina características.

### Correlación entre wearable y PSG

Contrastar características wearable con PSG. Una asociación débil no demuestra inutilidad ni equivalencia entre modalidades.

### 3.4.1. Asociación descriptiva con las etapas

Comparar el valor de una característica en una etapa frente al resto. AUC de rangos es la probabilidad de que el primero sea mayor, con medio peso para empates. El mapa usa 2×AUC−1: positivo mayor, negativo menor y cerca de cero sin dirección neta.

### 3.4.2. Tiempo y etapa

Comparar cuándo aparece cada etapa dentro del paciente. AUC temporal >0,5 indica tendencia posterior; <0,5, anterior. Los bloques de 30 minutos muestran proporciones con dos ponderaciones y cobertura; los últimos incluyen pocos pacientes.

## 3.5. Decisiones sobre características

Proponer representaciones y reconocer qué necesita comprobación predictiva.

### 3.5.1. Consistencia entre pacientes

Examinar si la dirección de una asociación se repite entre pacientes; no evaluable significa evidencia insuficiente para esa comparación.

### 3.5.2. Representaciones candidatas

Definir variantes originales, log1p y resúmenes combinados para comparar después.

## 3.6. Variación entre pacientes

Describir diferencias entre personas y etapas no observadas; no confundir ausencia en el registro con ausencia fisiológica.

## 3.7. Controles lógicos del ETL

Comprobar recuentos, fracciones, desviaciones, pureza y consistencia. Pasar controles no certifica calidad instrumental.

## 3.8. Síntesis antes de transformar

Resumir la ejecución actual, decisiones y límites antes de construir la copia candidata.

## 3.9. Transformación candidata y exportación

Exportar una copia de 26 columnas, con 22 predictores. log1p comprime valores altos sin eliminar ceros; ojos/piernas usan el máximo entre std y ACC la norma de tres std. Mantener intacto el ETL base.

### 3.9.1. Columnas finales

Consultar nombres, tipos, roles y descripciones exactos de las columnas candidatas.

# 4. Próximos pasos: modelado pendiente

Dividir por paciente, entrenar y evaluar modelos; comparar representaciones y escenarios sin usar la prueba para ajustar decisiones.

## Fuentes para explicar el trabajo

- Fuente: `CD_02_02_ETLv2`, tema extracción, transformación y carga.
- Fuente: `CD_02_03_Preprocesamiento`, temas tipos de variables, valores irregulares, transformación y reducción.
- Fuente: `CD_01_Aprendizaje Automatico`, tema aprendizaje supervisado y clasificación.

Las reglas concretas de alineación, imputación, recuperación parcial y resúmenes son decisiones del proyecto. El historial de Git conserva los detalles de las referencias teóricas utilizados anteriormente; esta reorganización no revalidó sus páginas.
