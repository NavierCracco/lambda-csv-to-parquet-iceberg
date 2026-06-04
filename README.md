# AWS Lambda: CSV to Parquet (Iceberg)

Este proyecto convierte tablas `landing_` del Glue Data Catalog en tablas Iceberg en formato Parquet usando Athena.

## Qué hace

- Busca tablas en Glue con el prefijo `landing_`.
- Crea tablas Iceberg llamadas `stg_<entidad>`.
- Copia datos a Parquet con compresión SNAPPY.
- Añade particiones `year`, `month` y `day` según la fecha de ejecución.

## Archivo principal

- `csv_to_parquet_converter.py`

## Cómo funciona

- Usa `boto3` para llamar a Glue y Athena.
- Lista tablas con `glue.get_tables(DatabaseName=...)`.
- Filtra tablas con prefijo `landing_`.
- Genera nombres de destino `stg_<entidad>`.
- Envía una consulta CTAS a Athena para crear la tabla Iceberg en S3.

Parámetros clave

- `database_name`: nombre genérico de la base de datos en Glue Data Catalog.
- `athena_results_path`: ruta S3 donde Athena guarda resultados y metadatos.
- `s3_target`: ruta S3 de destino para la tabla Iceberg (Parquet).

> Reemplaza estos valores con tu entorno real.

## Permisos IAM necesarios

Este ejemplo muestra los permisos mínimos para Glue, Athena y S3:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3DataLakePermissions",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::TU-BUCKET-DATA-LAKE",
        "arn:aws:s3:::TU-BUCKET-DATA-LAKE/*"
      ]
    },
    {
      "Sid": "GlueCatalogPermissions",
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase",
        "glue:GetTables",
        "glue:CreateTable",
        "glue:UpdateTable"
      ],
      "Resource": ["*"]
    },
    {
      "Sid": "AthenaExecutionPermissions",
      "Effect": "Allow",
      "Action": ["athena:StartQueryExecution", "athena:GetQueryExecution"],
      "Resource": ["*"]
    }
  ]
}
```

Consideraciones y riesgos

- Verificar que la versión/entorno de Athena usado soporta la creación de tablas Iceberg mediante CTAS en la configuración actual.
- CTAS en Athena puede implicar costes por escaneo de datos; optimizar particionado y formatos lo más pronto posible.
- La consulta añade particiones basadas en `CURRENT_DATE`, lo que significa que todos los registros resultantes obtendrán la partición del día en que se ejecute la consulta (no infiere particionado desde los datos originales).

## Despliegue

- Empaquetar este script como una función Lambda.
- Asignar un role IAM con los permisos mostrados arriba.
- Configurar `database_name`, `athena_results_path` y `s3_target` con valores reales.
- Usar la runtime de Lambda que ya incluye `boto3`.

## Siguientes pasos sugeridos

- Probar el script en un entorno de desarrollo con permisos limitados y una copia de datos.
- Añadir logging adicional y gestión de errores para monitorizar ejecuciones de Athena (comprobar estado de `QueryExecution`).
- Considerar particionado basado en columnas del dataset si el origen ya contiene fecha/hora.
