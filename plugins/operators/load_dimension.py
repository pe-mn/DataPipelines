# from airflow.hooks.postgres_hook import PostgresHook
# from airflow.models import BaseOperator
# from airflow.utils.decorators import apply_defaults

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.baseoperator import BaseOperator

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    truncate_sql = """
                    TRUNCATE TABLE {table}
                   """ 

    # @apply_defaults
    def __init__(self,
                 # Define operators params (with defaults) 
                 redshift_conn_id = "",
                 table = "",
                 sql_query = "",
                 truncate_table = False,
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        # Map params here
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.sql_query = sql_query
        self.truncate_table = truncate_table

    def execute(self, context):
        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        if self.truncate_table:
            formatted_truncate_sql = LoadDimensionOperator.truncate_sql.format(self.table)
            redshift_hook.run(formatted_insert_sql)
          
        self.log.info(f"Loading data into the dimension table {table}!!")
        redshift_hook.run(self.sql_query)
