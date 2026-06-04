import boto3
import time

def lambda_handler (event, context):

    glue = boto3.client(service_name='glue')
    athena = boto3.client(service_name='athena')

    database_name = 'name-of-your-glue-database' # Update with your actual Glue database name
    athena_results_path = 's3://your-bucket/athena-results/' # Update with your actual bucket and path

    print('Starting scan of the Glue Data Catalog...')

    try:
        res = glue.get_tables(DatabaseName = database_name)
        tables = res.get('TableList', [])

        for table in tables:
            table_name = table['Name']

            if table_name.startswith('landing_'):
                
                entity_name = table_name.replace('landing_', '')

                new_table_name = f"stg_{entity_name}"
                s3_target = f"s3://your-bucket/staging/{entity_name}/" # Update with your actual bucket and path

                query = f'''
                        CREATE TABLE IF NOT EXISTS "{database_name}"."{new_table_name}"
                        WITH (
                            table_type = 'ICEBERG',
                            is_external = false,
                            format = 'PARQUET',
                            write_compression = 'SNAPPY',
                            partitioning = ARRAY['year', 'month', 'day'],
                            location = '{s3_target}'
                        )
                        AS SELECT
                            *,
                            CAST(YEAR(CURRENT_DATE) AS VARCHAR) AS year,
                            CAST(MONTH(CURRENT_DATE) AS VARCHAR) AS month,
                            CAST(DAY(CURRENT_DATE) AS VARCHAR) AS day
                        FROM "{database_name}"."{table_name}";
                    '''
                
                print(f"Sending query to Athena for: {new_table_name}")

                athena.start_query_execution(
                    QueryString=query,
                    QueryExecutionContext={'Database': database_name},
                    ResultConfiguration={'OutputLocation': athena_results_path}
                )

                time.sleep(1)

        return {
            'statusCode': 200,
            'body': 'Success'
        }
    
    except Exception as e:
        print(f"Execution error: {str(e)}")
        raise e