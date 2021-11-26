from datetime import datetime
from flask import request
from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import inputs

temperature_readings = []


class TemperatureReading(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('sensorId',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('temperature',
                        type=int,
                        required=True,
                        help="This field cannot be blank."
                        )
    parser.add_argument('time',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        #help="Invalid Date/Time format. Expected ISO 8601 Date/Time format (YYYY-MM-DDTHH:MM:SS)."
                        )

    def put(self):
        data = TemperatureReading.parser.parse_args()

        temperature_reading = {
            'sensorId': data['sensorId'],
            'temperature': data['temperature'],
            'time': data['time']
        }
        temperature_readings.append(temperature_reading)
        return temperature_reading
