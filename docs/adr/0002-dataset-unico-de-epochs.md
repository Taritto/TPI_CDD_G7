---
status: accepted
date: 2026-09-28
---

# Generar un único dataset consolidado de epochs

## Implementación vigente

Implementado en 3.1–3.2 y exportaciones de 3.9: un dataset base consolidado, con clave `(patient_id, epoch)`, auditoría, descartes y manifiesto. Las dimensiones de la ejecución de referencia están en [entrega 2](../entrega-02/README.md). El formato implementado es CSV; Parquet sigue siendo una alternativa, no una salida existente.

Fuente: [notebook principal](../../temporal_version_tp_cdd.ipynb).

## Decisión y motivo

Consolidar los epochs en un único dataset base, ordenado por paciente y epoch. La clave `(patient_id, epoch)` identifica una observación; no eliminar por `patient_id`, porque cada persona aporta múltiples ventanas legítimas.

## Estructura y claves

Cada señal aporta `*_mean`, `*_median`, `*_std`, `*_n_valid` y `*_missing_frac`. Los dos últimos son indicadores de cobertura, no mediciones fisiológicas adicionales. El ETL también conserva `TIMESTAMP`, `tiempo_relativo_segundos`, `Sleep_Stage`, `porcentaje_pureza`, `porcentaje_pureza_original` y `etiqueta_imputada`, además de la clave.

La unicidad se comprueba por `(patient_id, epoch)` y por instante de inicio dentro del paciente. Dos epochs distintos pueden tener valores iguales sin ser duplicados. La exportación reemplaza el CSV de una ejecución; no acumula filas de corridas anteriores. Un único dataset simplifica el modelado frente a mantener una tabla completa por paciente.

## Salidas y reproducción

Se exportan `dataset_epochs_v1.csv`, `auditoria_epochs.csv`, `epochs_descartados.csv` y `manifest_etl_v1.json`. La auditoría registra inclusión, exclusión, segmentos recuperados y etiquetas inferidas.

Reutilizar caché solo cuando coincidan fuentes y reglas y pase su validación. En una sesión nueva de Kaggle hay que adjuntar las salidas guardadas para reutilizarlas; `/kaggle/working` no garantiza persistencia entre sesiones. No concatenar base y candidato como observaciones distintas.
