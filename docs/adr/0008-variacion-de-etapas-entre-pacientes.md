# Variación de etapas entre pacientes

**Estado de implementación:** parcial. La sección 3.6 del notebook produce un resumen por paciente con duración válida y tramo observado, recuentos y porcentajes por etapa, etapas ausentes, primera latencia REM desde el primer epoch de sueño, transiciones entre epochs contiguos y saltos de epoch. Integra fragmentos, descartes y continuidad de la auditoría cuando están disponibles, además de cobertura media de señales seleccionadas. Grafica distribuciones globales de proporciones, duración y latencia REM; no crea un hipnograma por paciente ni excluye registros. Se verificaron sintaxis y casos sintéticos con REM observado, REM ausente y huecos. Falta ejecutar e interpretar el resumen con los pacientes definitivos; cualquier revisión de casos particulares requerirá evidencia de etiquetas y calidad.

Un paciente con REM temprano, sin REM observado o sin N3 no se excluirá por ese hecho. Puede representar variación real, duración insuficiente, etapas no observadas, etiquetado o calidad de registro; hace falta evidencia antes de atribuir una causa. Estos casos se marcarán para revisión, no para eliminación automática. Una exclusión requerirá un problema de registro o etiquetas verificable y una justificación trazable.

## Resumen por paciente

Construir una tabla compacta con `patient_id`, duración válida y número de epochs, recuento y proporción de W/N1/N2/N3/R, etapas ausentes, primera aparición de REM y número de transiciones entre etiquetas consecutivas. Acompañar los indicadores con cobertura/calidad de señales y fragmentos o epochs descartados. Definir de forma explícita el origen temporal de la latencia REM (por ejemplo, desde el primer epoch de sueño, no automáticamente desde el comienzo del archivo). Si REM no aparece, registrar «no observado», nunca latencia cero. Un registro más corto tiene menor oportunidad de mostrar etapas tardías; interpretar proporciones y latencias considerando duración y tamaños de muestra.

## Visualización y revisión

Mostrar un resumen global entre pacientes, no un hipnograma por cada uno: distribución de proporciones por etapa, duración y latencia REM cuando sea definible. Inspeccionar individualmente solo los casos señalados por reglas transparentes y comprobar sus etiquetas, continuidad temporal y calidad de señal. Las comparaciones deben informar cuántos pacientes y epochs sustentan cada conclusión.

## Límite para el modelado

Las proporciones, latencia REM y transiciones calculadas con `Sleep_Stage` son descripciones/auditoría del registro, no predictores de un modelo que intenta predecir esa misma etiqueta; usarlas sería fuga de información. Separar entrenamiento, validación y prueba por paciente. Al construir las particiones, comprobar cobertura de etapas —en especial clases minoritarias— sin elegir ni modificar la prueba final según el desempeño observado. La heterogeneidad entre pacientes debe reflejarse en la evaluación, no ocultarse con exclusiones por desviarse del promedio.
