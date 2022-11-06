# https://knowledge.udacity.com/questions/755179

# from airflow.hooks.postgres_hook import PostgresHook
# from airflow.models import BaseOperator
# from airflow.utils.decorators import apply_defaults

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.baseoperator import BaseOperator
from helpers.sql_queries import SqlQueries


# You don't need to drop and re-create the fact table everytime the LoadFactOperator runs.
# You can create tables in the query editor.  --> of your Redshift cluster
# If you delete your cluster, you have to create tables 
# every time you create a new cluster -- In your create_tables.sql 
# you have all the table just copy and paste it into the query editor and run it.


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
        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        if self.truncate_table:
            formatted_truncate_sql = LoadFactOperator.truncate_sql.format(self.table)
            redshift_hook.run(formatted_insert_sql)
          
        self.log.info(f"Loading data into the fact table {table}!!")
        redshift_hook.run(self.sql_query)
        
