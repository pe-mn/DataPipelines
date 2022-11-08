# In Airflow 2.3.0 DummyOperator was deprecated in favor of EmptyOperator
from airflow.operators.empty import EmptyOperator

from operators.stage_redshift import StageToRedshiftOperator
from operators.load_fact import LoadFactOperator
# from operators.load_dimension import LoadDimensionOperator
from airflow.operators.subdag import SubDagOperator
from project.subdag import load_dim_tables
from operators.data_quality import DataQualityOperator

from helpers import SqlQueries

default_args = {
    'owner': 'udacity',
    'start_date': datetime(2018, 11, 1),
    'provide_context': True,
    'depends_on_past': False,
    'retries': 3,    
    'retry_delay': timedelta(minutes=5),
    'catchup': False, # When turned off, the scheduler creates a DAG run only for the latest interval.
    'email_on_retry': False,
    'dagrun_timeout': timedelta(minutes=60),  
}

# preset --> @hourl  |  cron --> 0 * * * *
# Run once an hour at the beginning of the hour	
dag = DAG('udac_example_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *',
          max_active_runs = 1
        )

start_operator = EmptyOperator(task_id='Begin_execution',  dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    table="staging_events",
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    s3_bucket="udacity-dend",
    s3_key="log_data/{{execution_date.year}}/{{execution_date.month}}/{{ ds }}-events.json",
    # s3_key="log_data/{{ execution_date.strftime('%Y') }}/{{ execution_date.strftime('%m') }}/{{ ds }}-events.json",
    region="us-west-2",
    file_format="JSON",
    jsonpath = "s3://udacity-dend/log_json_path.json",
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    table="staging_songs",
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    s3_bucket="udacity-dend",
    s3_key="song-data", # /A/A/A
    region="us-west-2",
    file_format="JSON",
    jsonpath='auto'
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id = "redshift",
    table = "songplays",
    sql_query = SqlQueries.songplay_table_insert,
    truncate_table = False,
)

dim_task_id = "Load_dim_tables"
load_dimention_tables = SubDagOperator(
    subdag = load_dim_tables(
                parent_dag_name="udac_example_dag",
                task_id=dim_task_id ,
                redshift_conn_id="redshift",
                truncate=False,
                default_args=default_args,
             ),       
    task_id=dim_task_id,
    dag=dag
)


#-----------------------------------------------------------------------
# QUALITY CHECKS
# ---------------
# run_quality_checks = DataQualityOperator(
#     task_id='Run_data_quality_checks',
#     dag=dag,
#     redshift_conn_id = "redshift",
#     tables = ["staging_songs", "staging_events", "songplays", "songs", "artists", "time", "users"]
# )

staging_quality_checks = DataQualityOperator(
    task_id='staging_quality_checks',
    dag=dag,
    redshift_conn_id = "redshift",
    tables = ["staging_songs", "staging_events"],
    dq_checks=[{'check_sql': "SELECT COUNT(*) FROM {}", 'threshold': 0, 'comparison': operator.gt}]
)

fact_quality_checks = DataQualityOperator(
    task_id='fact_quality_checks',
    dag=dag,
    redshift_conn_id = "redshift",
    tables = ["songplays"],
    dq_checks=[{'check_sql': "SELECT COUNT(*) FROM {}", 'threshold': 0, 'comparison': operator.gt}]
)

dim_quality_checks = DataQualityOperator(
    task_id='dim_quality_checks',
    dag=dag,
    redshift_conn_id = "redshift",
    tables = ["songs", "artists", "time", "users"],
    dq_checks=[{'check_sql': "SELECT COUNT(*) FROM {}", 'threshold': 0, 'comparison': operator.gt}]
)

end_operator = EmptyOperator(task_id='Stop_execution',  dag=dag)

#-----------------------------------------------------------------------
# TASK ORDERING
#---------------
# To make the diagram looks even more concise, you may combine the dependency assignments in a single line:
# op1 >> op2 >> [op3, op4] >> op5
start_operator >> [stage_events_to_redshift, stage_songs_to_redshift] >> staging_quality_checks
staging_quality_checks>>load_songplays_table>>fact_quality_checks>>end_operator 
staging_quality_checks>>load_dimention_tables>>dim_quality_checks>>end_operator 

# start_operator >> stage_events_to_redshift
# start_operator >> stage_songs_to_redshift

# stage_events_to_redshift >> staging_quality_checks
# stage_songs_to_redshift >> staging_quality_checks

# staging_quality_checks >> load_songplays_table
# load_songplays_table >> fact_quality_checks

# fact_quality_checks >> load_dimention_tables
# load_dimention_tables >> dim_quality_checks
# dim_quality_checks >> end_operator 




