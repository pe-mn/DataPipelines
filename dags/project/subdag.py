# https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html#subdags

from datetime import datetime, timedelta
from airflow import DAG

from operators.load_dimension import LoadDimensionOperator
# from operators.data_quality import DataQualityOperator

from helpers import SqlQueries

def load_dim_tables(
    parent_dag_name="udac_example_dag",
    task_id="Load_dim_tables" ,
    redshift_conn_id="redshift",
    truncate=False,
    *args, **kwargs):

    """
    Returns a SubDag that load the dimension tables 
    (users, songs, artists, time)
    """

    dag = DAG(
        f"{parent_dag_name}.{task_id}", **kwargs
    )

    load_user_dimension_table = LoadDimensionOperator(
        task_id='Load_user_dim_table',
        dag=dag,
        redshift_conn_id = redshift_conn_id,
        table = "users",
        sql_query = SqlQueries.user_table_insert,
        truncate_table = truncate,
    )

    load_song_dimension_table = LoadDimensionOperator(
        task_id='Load_song_dim_table',
        dag=dag,
        redshift_conn_id = redshift_conn_id,
        table = "songs",
        sql_query = SqlQueries.song_table_insert,
        truncate_table = truncate,
    )

    load_artist_dimension_table = LoadDimensionOperator(
        task_id='Load_artist_dim_table',
        dag=dag,   
        redshift_conn_id = redshift_conn_id,
        table = "artists",
        sql_query = SqlQueries.artist_table_insert,
        truncate_table = truncate,
    )

    load_time_dimension_table = LoadDimensionOperator(
        task_id='Load_time_dim_table',
        dag=dag,
        redshift_conn_id = redshift_conn_id,
        table = "time",
        sql_query = SqlQueries.time_table_insert,
        truncate_table = truncate,
    )

    return dag



# Some other tips when using SubDAGs:
# ------------------------------------
# - By convention, a SubDAG’s dag_id should be prefixed by the name of its parent DAG and a dot (parent.child)
# - You should share arguments between the main DAG and the SubDAG by passing arguments to the SubDAG operator 
# (as demonstrated above)
# - SubDAGs must have a schedule and be enabled. If the SubDAG’s schedule is set to None or @once,
#   the SubDAG will succeed without having done anything.
# - Clearing a SubDagOperator also clears the state of the tasks within it.
# - Marking success on a SubDagOperator does not affect the state of the tasks within it.
# - Refrain from using Depends On Past in tasks within the SubDAG as this can be confusing.
# - You can specify an executor for the SubDAG. It is common to use the SequentialExecutor 
#   if you want to run the SubDAG in-process and effectively limit its parallelism to one.
#   Using LocalExecutor can be problematic as it may over-subscribe your worker, running multiple tasks 
#   in a single slot.


























