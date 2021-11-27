from flask import Flask
from flask_restful import Api

from resources.temperature import TemperatureReading
from resources.stats import Stats


app = Flask(__name__)
api = Api(app)

api.add_resource(TemperatureReading, '/api/temperature')
api.add_resource(Stats, '/api/stats')
