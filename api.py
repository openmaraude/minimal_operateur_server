from flask import Flask, request, abort, current_app
from flask.ext import restful

app = Flask(__name__)
api = restful.Api(app)

class Pong(restful.Resource):
    def post(self):
       for h in request.headers.keys():
           current_app.logger.info("{}: {}".format(h, request.headers.get(h)))
       json = request.get_json()
       if not 'data' in json or len(json['data']) != 1 or 'status' not in json['data'][0]:
           abort(400)
       json['data'][0]['status'] = 'received_by_taxi'
       json['data'][0]['taxi_phone_number'] = 'aaa'
       return json, 201

class PongAPIKEY(restful.Resource):
    def post(self):
       apikey = request.headers.get('X-API-KEY', None)
       if not apikey:
           abort(400)
       if apikey != 'xxx':
            abort(403)
       json = request.get_json()
       if not 'data' in json or len(json['data']) != 1 or 'status' not in json['data'][0]:
           abort(400)
       json['data'][0]['status'] = 'received_by_taxi'
       json['data'][0]['taxi_phone_number'] = 'aaa'
       return json, 201

class PongEmpty(restful.Resource):
    def post(self):
        return {}, 201

class PongEmptyTaxi(restful.Resource):
    def post(self):
        return {'data': [{}]}, 201

api.add_resource(Pong, '/hail/')
api.add_resource(PongAPIKEY, '/hail_apikey/')
api.add_resource(PongEmpty, '/hail_empty/')
api.add_resource(PongEmptyTaxi, '/hail_empty_taxi/')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
