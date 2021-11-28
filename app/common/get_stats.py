import os

import botocore
import boto3
import logging

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
            ]
        )
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'LimitExceededException':
            logger.warn(
                'API call limit exceeded; backing off and retrying...')
        else:
            raise error

    return {
        "Maximum": int(current_stats_response['Item']['maximum']['N']),
        "Minimum": int(current_stats_response['Item']['minimum']['N']),
        "total_temperature_sum": int(current_stats_response['Item']['total_temperature_sum']['N']),
        "total_readings_count": int(current_stats_response['Item']['total_readings_count']['N'])
    }
