from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import inputs

import botocore
import boto3
import logging

from resources.stats import Stats
from common.get_stats import get_stats
from common.non_empty_string import non_empty_string


client = boto3.client('dynamodb')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


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
            save_temperature_reading = client.put_item(
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

        current_stats = get_stats()

        maximum_temperature = max(
            data['temperature'], current_stats['Maximum'])
        minimum_temperature = min(
            data['temperature'], current_stats['Minimum'])

        update_stats_response = Stats.update_stats(
            data['temperature'], maximum_temperature, minimum_temperature)

        return {"message": "Temperature reading recorded successfully"}
