from flask import Flask
from flask_restful import Api
from resources.temperature import Temperature
from resources.stats import Stats

app = Flask(__name__)
api = Api(app)

api.add_resource(Temperature, '/api/temperature')
api.add_resource(Stats, '/api/stats')

app.run(port=5000, debug=True)
