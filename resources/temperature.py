from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import inputs

import boto3

client = boto3.client('dynamodb')


class TemperatureReading(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('sensorId',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('timestamp',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        #help="Invalid Date/Time format. Expected ISO 8601 Date/Time format (YYYY-MM-DDTHH:MM:SS)."
                        )
    parser.add_argument('temperature',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def put(self):
        data = TemperatureReading.parser.parse_args()

        save_temperature_reading_response = client.put_item(
            TableName='temperature_readings',
            Item={
                'sensor_id': {
                    'S': data['sensorId']
                },
                'timestamp': {
                    'S': data['timestamp']
                },
                'temperature': {
                    'N': data['temperature']
                }
            }
        )

        if save_temperature_reading_response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {'message: "Error saving temperature reading to database. Please try again"'}, 500

        current_stats_response = client.get_item(
            TableName='temperature_readings_aggregation',
            Key={
                'aggregation_period': {
                    'S': 'total'
                },
            },
            AttributesToGet=[
                'total_readings_count',
                'maximum',
                'minimum',
                'average'
            ]
        )

        return {
            "message": "Temperature reading recorded successfully",
            "currentStats": {
                "maximum": current_stats_response['Item']['maximum']['N'],
                "minimum": current_stats_response['Item']['minimum']['N'],
                "average": current_stats_response['Item']['average']['N']
            }
        }
