# Decisiones del proyecto (ADR)

Cada ADR registra qué se decidió, por qué y sus consecuencias. Consultar **Implementación vigente** para el estado actual y las secciones siguientes para su justificación. Las versiones anteriores se consultan en Git. Los resultados de cada entrega están en su propia carpeta.

- [0001-uso-de-apneas-e-indicadores-de-sleep-stage.md](0001-uso-de-apneas-e-indicadores-de-sleep-stage.md)
- [0002-dataset-unico-de-epochs.md](0002-dataset-unico-de-epochs.md)
- [0003-epochs-de-30-segundos.md](0003-epochs-de-30-segundos.md)
- [0004-interpretacion-y-generalizacion-del-eda.md](0004-interpretacion-y-generalizacion-del-eda.md)
- [0005-deteccion-y-tratamiento-de-valores-anomalos.md](0005-deteccion-y-tratamiento-de-valores-anomalos.md)
- [0006-mapas-de-asociacion-y-variables-correlacionadas.md](0006-mapas-de-asociacion-y-variables-correlacionadas.md)
- [0007-revision-y-seleccion-de-caracteristicas.md](0007-revision-y-seleccion-de-caracteristicas.md)
- [0008-variacion-de-etapas-entre-pacientes.md](0008-variacion-de-etapas-entre-pacientes.md)
- [0009-distribuciones-y-desbalance-de-etapas.md](0009-distribuciones-y-desbalance-de-etapas.md)
- [0010-rangos-validos-y-recorte-de-extremos.md](0010-rangos-validos-y-recorte-de-extremos.md)
- [0011-modelado-posterior-a-la-entrega-etl.md](0011-modelado-posterior-a-la-entrega-etl.md)
- [0012-etiquetas-missing-y-segmentos-alineados.md](0012-etiquetas-missing-y-segmentos-alineados.md)

Actualizar el ADR si cambia su implementación. Si se reemplaza una decisión, registrar el motivo y su sucesora. No duplicar estas reglas dentro de cada entrega.

Los ADR guardan reglas y motivos; la ficha de cada entrega guarda dimensiones y resultados. Una implementación comprobada no implica superioridad predictiva. Las propuestas de modelos y transformaciones se mantienen como propuestas hasta evaluarlas.

Metadatos: `status: accepted` indica que la regla fue adoptada, no que su evaluación predictiva haya terminado. `date` conserva la fecha registrada; donde faltaba, se recuperó la fecha de incorporación del ADR en Git.
