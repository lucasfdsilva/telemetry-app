import os

from flask_restful import Resource

import botocore
import boto3
import logging


client = boto3.client('dynamodb')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class Stats(Resource):

    def get_stats():
        try:
            current_stats_response = client.get_item(
                TableName=f"{os.environ['PREFIX']}-temperature-readings-aggregation",
                Key={
                    'aggregation_period': {
                        'S': 'total'
                    },
                },
                AttributesToGet=[
                    'maximum',
                    'minimum',
                    'total_temperature_sum',
                    'total_readings_count',
                ],
                ConsistentRead=True
            )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                logger.warn(
                    'API call limit exceeded; backing off and retrying...')
            else:
                raise error

        maximum = int(current_stats_response['Item']['maximum']['N'])
        minimum = int(current_stats_response['Item']['minimum']['N'])
        total_temperature_sum = int(
            current_stats_response['Item']['total_temperature_sum']['N'])
        total_readings_count = int(
            current_stats_response['Item']['total_readings_count']['N'])

        return {
            "Maximum": maximum,
            "Minimum": minimum,
            "total_temperature_sum": total_temperature_sum,
            "total_readings_count": total_readings_count
        }

    def update_stats(count_increment_value, temperature, maximum_temperature, minimum_temperature):

        try:
            update_stats_response = client.update_item(
                TableName=f"{os.environ['PREFIX']}-temperature-readings-aggregation",
                Key={
                    'aggregation_period': {
                          'S': 'total'
                    }
                },
                UpdateExpression="""ADD total_readings_count :count_increment_value,
                                total_temperature_sum :temperature_value
                                SET maximum= :highest_temperature,
                                minimum= :lowest_temperature""",
                ExpressionAttributeValues={
                    ':count_increment_value': {
                        "N": str(count_increment_value)
                    },
                    ':temperature_value': {
                        "N": str(temperature)
                    },
                    ':highest_temperature': {
                        "N": str(maximum_temperature)
                    },
                    ':lowest_temperature': {
                        "N": str(minimum_temperature)
                    },
                },
                ReturnValues="UPDATED_NEW"
            )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                logger.warn(
                    'API call limit exceeded; backing off and retrying...')
            else:
                raise error

            return

    def get(self):

        current_stats = Stats.get_stats()

        if current_stats['total_readings_count'] > 0:
            average_temperature = round(current_stats['total_temperature_sum']
                                        / current_stats['total_readings_count'])
        else:
            average_temperature = 0

        return {
            "Maximum": current_stats['Maximum'],
            "Minimum": current_stats['Minimum'],
            "Average": average_temperature
        }
