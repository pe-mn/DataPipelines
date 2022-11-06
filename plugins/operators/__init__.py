from operators.stage_redshift import StageToRedshiftOperator
from operators.load_fact import LoadFactOperator
from operators.load_dimension import LoadDimensionOperator
from operators.data_quality import DataQualityOperator

from operators.s3_to_redshift import S3ToRedshiftOperator
from operators.has_rows import HasRowsOperator
from operators.facts_calculator import FactsCalculatorOperator

        


__all__ = [
    'StageToRedshiftOperator',
    'LoadFactOperator',
    'LoadDimensionOperator',
    'DataQualityOperator',
    'FactsCalculatorOperator',
    'HasRowsOperator',
    'S3ToRedshiftOperator'
]

# ------------------------------------------------------------------

# from airflow.plugins_manager import AirflowPlugin
# import operators 

# Class UdacityPlugin(AirflowPlugin):
#     name="udacity_plugin"
#     operators=[operators.StageToRedshiftOperator,
#                operators.LoadFactOperator,
#                operators.LoadDimensionOperator,
#                operators.DataQualityOperator]
#     helpers = [
#         helpers.SqlQueries
#     ]
