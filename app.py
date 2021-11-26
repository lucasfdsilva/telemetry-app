from flask import Flask
from flask_restful import Api

from resources.temperature import TemperatureReading

app = Flask(__name__)
api = Api(app)

api.add_resource(TemperatureReading, '/api/temperature')

app.run(port=5000, debug=True)
