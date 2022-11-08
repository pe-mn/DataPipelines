# Note:
# Stage --> Means moving from S3 to Redshift

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
from airflow.models.baseoperator import BaseOperator

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    template_fields = ("s3_key",)
    # We added s3_key to template_fields in our custom operator to render the execution_date
    # in our stage events task

# Use one of the following to provide authorization for the COPY command:
#     - IAM_ROLE parameter
#     - ACCESS_KEY_ID and SECRET_ACCESS_KEY parameters
#     - CREDENTIALS clause

# Valid values for avro_option are as follows:
#     - 'auto'
#     - 'auto ignorecase'
#     - 's3://jsonpaths_file' 

    # This is a Class Attribute
    copy_sql = """
            COPY {}
            FROM '{}'
            ACCESS_KEY_ID '{}'
            SECRET_ACCESS_KEY '{}'
            REGION '{}'
            {} '{}' 
    """     

    def __init__(self,
                 # Define operators params (with defaults) 
                 redshift_conn_id = "",
                 aws_credentials_id = "",
                 table = "",
                 s3_bucket = "",
                 s3_key = "",
                 region="",
                 file_format="JSON",
                 jsonpath = 'auto',
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        # Map params 
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table = table
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.region= region
        self.file_format = file_format
        self.jsonpath = jsonpath

    def execute(self, context):
        """
        Copy data from S3 buckets to redshift cluster into staging tables.
            - redshift_conn_id: redshift cluster connection
            - aws_credentials_id: AWS connection
            - table: redshift cluster table name
            - s3_bucket: S3 bucket name holding source data
            - s3_key: S3 key files of source data
            - file_format: source file format - options JSON, CSV
        """
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
            self.region,
            self.file_format,
            self.jsonpath,
            # self.ignore_headers,
            # self.delimiter,
        )
        redshift_hook.run(formatted_sql)

        self.log.info(f"SUCCESS: Copying {self.table} from S3 to Redshift")





