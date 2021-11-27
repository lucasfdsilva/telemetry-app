from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import inputs

import botocore
import boto3
import logging


client = boto3.client('dynamodb')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def non_empty_string(string):
    if not string:
        raise ValueError("String must not be empty.")
    return string


class TemperatureReading(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('sensorId',
                        type=non_empty_string,
                        required=True,
                        nullable=False,
                        trim=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('timestamp',
                        type=inputs.datetime_from_iso8601,
                        required=True,
                        nullable=False,
                        trim=True,
                        help="Expected ISO 8601 Date/Time format. e.g. 2021-11-26T18:10:00"
                        )
    parser.add_argument('temperature',
                        type=int,
                        required=True,
                        trim=True,
                        help="This field cannot be blank."
                        )

    def put(self):
        data = TemperatureReading.parser.parse_args()

        try:
            save_temperature_reading_response = client.put_item(
                TableName='temperature_readings',
                Item={
                    'sensor_id': {
                        'S': data['sensorId']
                    },
                    'timestamp': {
                        'S': str(data['timestamp'])
                    },
                    'temperature': {
                        'N': str(data['temperature'])
                    }
                }
            )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'LimitExceededException':
                logger.warn(
                    'API call limit exceeded; backing off and retrying...')
            else:
                raise error

        current_stats_response = client.get_item(
            TableName='temperature_readings_aggregation',
            Key={
                'aggregation_period': {
                    'S': 'total'
                },
            },
            AttributesToGet=[
                'maximum',
                'minimum',
            ]
        )

        print(current_stats_response)

        maximum_temperature = max(
            data['temperature'], int(current_stats_response['Item']['maximum']['N']))
        minimum_temperature = min(
            data['temperature'], int(current_stats_response['Item']['minimum']['N']))

        print(minimum_temperature)

        update_stats_response = client.update_item(
            TableName='temperature_readings_aggregation',
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
                    "N": "1"
                },
                ':temperature_value': {
                    "N": str(data['temperature'])
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

        return {
            "message": "Temperature reading recorded successfully",
            "currentStats": {
                "maximum": update_stats_response['Attributes']['maximum']['N'],
                "minimum": update_stats_response['Attributes']['minimum']['N'],
                "total_temperature_sum": update_stats_response['Attributes']['total_temperature_sum']['N'],
                "total_readings_count": update_stats_response['Attributes']['total_readings_count']['N']
            }
        }
