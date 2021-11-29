import os

import botocore
import boto3
import logging

from resources.stats import Stats

client = boto3.client('dynamodb')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


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

    print(current_stats_response)

    if current_stats_response['Item'] is None:
        Stats.update_stats(0, 0,
                           0, 0)
        maximum = 0
        minimum = 0
        total_temperature_sum = 0
        total_readings_count = 0
    else:
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
