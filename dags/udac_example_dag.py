# https://airflow-tutorial.readthedocs.io/en/latest/setup.html
# https://github.com/puckel/docker-airflow
# https://airflow-tutorial.readthedocs.io/en/latest/first-airflow.html

# The provide_context only belongs Python operator.
# Other operator s are free to use the context argument.

from datetime import datetime, timedelta
import os
from airflow import DAG

#----------------------------------------------------------------------------------------------
# from airflow.operators.dummy_operator import DummyOperator # Depricated
# https://airflow.apache.org/docs/apache-airflow/2.2.5/_api/airflow/operators/dummy/index.html
# from airflow.operators.dummy import DummyOperator
# Operator that does literally nothing. It can be used to group tasks in a DAG.
# The task is evaluated by the scheduler but never processed by the executor.

# n Airflow 2.3.0 DummyOperator was deprecated in favor of EmptyOperator
from airflow.operators.empty import EmptyOperator
#----------------------------------------------------------------------------------------------

# https://stackoverflow.com/questions/43907813/cant-import-airflow-plugins
# from airflow.operators.udacity_plugin import (StageToRedshiftOperator, LoadFactOperator,
#                                               LoadDimensionOperator, DataQualityOperator)

from operators.stage_redshift import StageToRedshiftOperator
from operators.load_fact import LoadFactOperator
from operators.load_dimension import LoadDimensionOperator
from operators.data_quality import DataQualityOperator

from helpers import SqlQueries

# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')

default_args = {
    'owner': 'udacity',
    'start_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,    
    'retry_delay': timedelta(minutes=5),
    'catchup': False, # When turned off, the scheduler creates a DAG run only for the latest interval.
    'email_on_retry': False,
    # 'email': ['***']    
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
    # s3_key="log_data/{execution_date.year}/{execution_date.month}/{{ ds }}-events.json",
    s3_key="log_data/{{ execution_date.strftime('%Y') }}/{{ execution_date.strftime('%m') }}/{{ ds }}-events.json",
    json="auto",
    # region="us-west-2",
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    table="staging_songs",
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    s3_bucket="udacity-dend",
    s3_key="song-data/A/A/A", # /A/A/A
    json="auto",
    # region="us-west-2",
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id = "redshift",
    table = "songplays",
    sql_query = SqlQueries.songplay_table_insert,
    truncate_table = False,
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id = "redshift",
    table = "users",
    sql_query = SqlQueries.user_table_insert,
    truncate_table = False,
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id = "redshift",
    table = "songs",
    sql_query = SqlQueries.song_table_insert,
    truncate_table = False,
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,   
    redshift_conn_id = "redshift",
    table = "artists",
    sql_query = SqlQueries.artist_table_insert,
    truncate_table = False,
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id = "redshift",
    table = "time",
    sql_query = SqlQueries.time_table_insert,
    truncate_table = False,
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    tables = ["staging_songs", "staging_events", "songplays", "songs", "artists", "time", "users"]
)

end_operator = EmptyOperator(task_id='Stop_execution',  dag=dag)


# TASK ORDERING
#---------------
start_operator >> stage_events_to_redshift
start_operator >> stage_songs_to_redshift

stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table

load_songplays_table >> load_user_dimension_table
load_songplays_table >> load_song_dimension_table
load_songplays_table >> load_artist_dimension_table
load_songplays_table >> load_time_dimension_table

load_user_dimension_table >> run_quality_checks
load_song_dimension_table >> run_quality_checks
load_artist_dimension_table >> run_quality_checks
load_time_dimension_table >> run_quality_checks

run_quality_checks >> end_operator 