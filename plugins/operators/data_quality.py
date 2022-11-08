import operator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.baseoperator import BaseOperator

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    def __init__(self,
                 # Define operators params (with defaults) 
                 redshift_conn_id = "",
                 tables=[],
                 dq_checks=[], # List of dictionaries
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        # Map params 
        self.redshift_conn_id = redshift_conn_id
        self.tables = tables
        self.dq_checks = dq_checks

    def execute(self, context):
        """
        Perform Data quality check, to make sure tables are not empty
        """        
        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        for table in self.tables:  
            for i, dq_check in enumerate(self.dq_checks):
                self.log.info(f'#{i} Data quality check on table {table}')
                records = redshift_hook.get_records(dq_check['check_sql'].format(table))
                if not (dq_check['comparison'](records[0][0], dq_check['threshold'])): 
                    raise ValueError(f"#{i}Data quality check on table {table} failed.") #  {put explanation of the error here}

            self.log.info(f'SUCCESS: Data quality check on table {table} passed with {records[0][0]} records')