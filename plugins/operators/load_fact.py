from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.baseoperator import BaseOperator
from helpers.sql_queries import SqlQueries


class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'

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

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        # Map params here
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.sql_query = sql_query
        self.truncate_table = truncate_table


    def execute(self, context):
        """
        Load data into the fact table (songplays)
        """ 
        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        if self.truncate_table:
            self.log.info(f"TRUNCATE table {self.table}!!")
            formatted_truncate_sql = LoadFactOperator.truncate_sql.format(self.table)
            redshift_hook.run(formatted_truncate_sql)
          
        self.log.info(f"LOADING data into the dimension table {self.table}")
        redshift_hook.run(self.sql_query)
        self.log.info(f"SUCCESS: Loaded data into the dimension table {self.table}")
        
