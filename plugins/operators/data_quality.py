# from airflow.hooks.postgres_hook import PostgresHook
# from airflow.models import BaseOperator
# from airflow.utils.decorators import apply_defaults

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.baseoperator import BaseOperator

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    # @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) 
                 redshift_conn_id = "",
                 tables=[],
                 table="",
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        # Map params 
        self.redshift_conn_id = redshift_conn_id
        self.tables = tables
        self.table = table

    def execute(self, context):
        # self.log.info('DataQualityOperator not implemented yet')
        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        for self.table in self.tables:       
            records = redshift_hook.get_records(f"SELECT COUNT(*) FROM {self.table}")

            if len(records < 1) or len(records[0] < 1):
                raise ValueError(f"Data quality check failed. {self.table} returned no results")
            if records[0][0] < 1:  # records[0][0] --> num_records
                raise ValueError(f"Data quality check failed. {self.table} contained 0 rows")

            self.log.info(f'Data quality check on table {self.table} passed with {records[0][0]} records')

