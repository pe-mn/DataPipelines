# Note:
# Stage --> Meaning moving from S3 to Redshift

# https://knowledge.udacity.com/questions/659765
# https://knowledge.udacity.com/questions/685378
# https://knowledge.udacity.com/questions/892503
# https://www.geeksforgeeks.org/difference-between-delete-and-truncate/

# https://knowledge.udacity.com/questions/448122
# A registered template field can utilize the environment variables of Airflow during execution.
# An example of this is trying to fetch the files that has the date as a part of the name 
# (file_name_20200113). You will use the s3_key variable to do this by parsing the date during
# execution as follows (file_name_{{ ds_nodash }}). This makes the parsing of files dynamic 
# and fetches the daily files without any intervention from the user.


# # from airflow.hooks.postgres_hook import PostgresHook
# from airflow.models import BaseOperator
# from airflow.utils.decorators import apply_defaults

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
from airflow.models.baseoperator import BaseOperator

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    template_fields = ("s3_key",)
    # We added s3_key to template_fields in our custom operator to render the execution_date
    # in our stage events tast 

# https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-authorization.html
# Use one of the following to provide authorization for the COPY command:
#     - IAM_ROLE parameter
#     - ACCESS_KEY_ID and SECRET_ACCESS_KEY parameters
#     - CREDENTIALS clause

    # This is a Class Attribute
    copy_sql = """
        COPY {}
        FROM '{}'
        ACCESSS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        IGNOREHEADER {}
        DELIMITER '{}'
        JSON '{}'
    """
    # REGION '{}'
    # COMPUPDATE OFF
    # TIMEFORMAT 'epochmillisecs'


    # @apply_defaults
    def __init__(self,
                 # Define operators params (with defaults) 
                 redshift_conn_id = "",
                 aws_credentials_id = "",
                 table = "",
                 s3_bucket = "",
                 s3_key = "",
                 delimiter = ",",
                 ignore_headers = 1,
                 json="auto",
                #  region="",
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        # Map params 
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table = table
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.delimiter = delimiter
        self.ignore_headers = ignore_headers
        self.json = json
        # self.region=region

    def execute(self, context):
        aws_hook = AwsBaseHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        self.log.info("Clearing data destination Redshift table")
        redshift_hook.run(f"TRUNCATE TABLE {self.table}") # Faster than DELETE FROM {self.table}

        # Note: 
        # -----
        # Here we need the created AWS IAM user credentials
        # to allow Redshift Cluster to access S3
        self.log.info("Copying data from s3 to Redshift")
        rendered_key = self.s3_key.format(**context)
        s3_path = f"s3://{self.s3_bucket}/{rendered_key}"
        formatted_sql = StageToRedshiftOperator.copy_sql.format(
            self.table,
            s3_path,
            credentials.access_key,
            credentials.secret_key,
            self.ignore_headers,
            self.delimiter,
            self.json
        )
        redshift_hook.run(formatted_sql)





