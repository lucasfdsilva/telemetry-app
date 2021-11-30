from flask import Flask
from flask_restful import Api

from resources.home import Home
from resources.temperature import TemperatureReading
from resources.stats import Stats


app = Flask(__name__)
api = Api(app)

api.add_resource(Home, '/')
api.add_resource(Stats, '/api/stats')
api.add_resource(TemperatureReading, '/api/temperature')
