from flask import Flask, request, abort, current_app, g
import flask_restx as restplus
import requests

app = Flask(__name__)
api = restplus.Api(app)

class Pong(restplus.Resource):
    def post(self):
       for h in request.headers.keys():
           current_app.logger.info("{}: {}".format(h, request.headers.get(h)))
       json = request.get_json()
       if not 'data' in json or len(json['data']) != 1 or 'status' not in json['data'][0]:
           abort(400)
       json['data'][0]['status'] = 'received_by_taxi'
       json['data'][0]['taxi_phone_number'] = 'aaa'
       g.last_hail_id = json['data'][0]['id']
       return json, 201

class PongAPIKEY(restplus.Resource):
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

class PongEmpty(restplus.Resource):
    def post(self):
        return {}, 201

class PongEmptyTaxi(restplus.Resource):
    def post(self):
        return {'data': [{}]}, 201

class PongLastHail(restplus.Resource):
    def post(self):
       json = request.get_json()
       apikey = json['apikey']
       server = json['server'].rstrip("/")
       status = json['status']

       payload = {"data": [{"status": status}]}
       if status == 'accepted_by_taxi':
           payload = payload['data'][0]['taxi_phone_number'] = '010101010'

       r = request.put(
           "{}/hails/{}/".format(server, g.last_hail_id),
           json=payload,
           headers={"Accept": "application/json", "X-VERSION": "2", "X-API-KEY": apikey}
       )

       return r.json(), 200



api.add_resource(Pong, '/hail/')
api.add_resource(PongAPIKEY, '/hail_apikey/')
api.add_resource(PongEmpty, '/hail_empty/')
api.add_resource(PongEmptyTaxi, '/hail_empty_taxi/')
api.add_resource(PongLastHail, '/last_hail/_set_status')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
