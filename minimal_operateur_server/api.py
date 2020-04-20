import json
import os
import time
import urllib

from flask import Flask, jsonify, request
from marshmallow import EXCLUDE, fields, Schema, validate
from flask_rq2 import RQ
import requests


app = Flask(__name__)
app.url_map.strict_slashes = False

rq = RQ()


def create_app():
    app.config.from_object('minimal_operateur_server.default_settings')
    # Override default configuration with the file specified in the environment
    # variable API_SETTINGS.
    if os.getenv('API_SETTINGS'):
        app.config.from_envvar('API_SETTINGS')
    rq.init_app(app)
    return app


@rq.job
def notify_taxi(taxi_id, hail_id, customer_lon, customer_lat, customer_address,
                customer_phone_number):
    """Notify taxi of the incoming hail."""
    # Here, we should notify the taxi that he has a hail request for example
    # by sending a phone notification. When the notification is received, we
    # update the hail status.
    # In this example, we just sleep 0.5 seconds.
    time.sleep(0.5)

    # Synchronously update hail status to "received_by_taxi".
    update_hail(hail_id, 'received_by_taxi')

    # Now we should wait for the taxi response which should accept or refuse
    # the hail before the next 30 seconds.
    # For this example purpose, we call the API endpoint /answer ourselves and
    # accept the hail. In real-world, the taxi application should call the
    # endpoint within 10 seconds.
    app.test_client().post(
        '/answer/%s/%s' % (taxi_id, hail_id),
        data=json.dumps({'status': 'accept'}),
        content_type='application/json'
    )


@rq.job
def update_hail(hail_id, new_status, taxi_phone_number=None):
    """Call api.taxi to update the status of a hail. If new_status is
    "accepted_by_taxi", taxi_phone_number must be provided."""

    # https://api.taxi/hails/:hail_id
    url = urllib.parse.urljoin(app.config['API_TAXI_URL'], 'hails/%s' % hail_id)

    payload = {'status': new_status}
    if taxi_phone_number:
        payload['taxi_phone_number'] = taxi_phone_number

    # Make the PUT request. The expected JSON data is an object with a key
    # "data", containing a list of one element.
    #
    # This element contains the status and optionally the taxi_phone_number.
    #
    # The headers X-Version and X-Api-Key must also be provided.
    response = requests.put(url, json={
        'data': [payload]
    }, headers={
        'X-Version': '3',
        'X-Api-Key': app.config['API_TAXI_KEY']
    })


@app.route('/')
def index():
    return jsonify('API to receive hails from le.taxi')


class HailTaxiSchemaContent(Schema):
    class Meta:
        """Allow extra fields."""
        unknown = EXCLUDE

    id = fields.String(required=True)


class HailSchemaContent(Schema):
    class Meta:
        """Allow extra fields."""
        unknown = EXCLUDE

    customer_lon = fields.Float(required=True)
    customer_lat = fields.Float(required=True)
    customer_address = fields.String(required=True)
    customer_phone_number = fields.String(required=True)
    id = fields.String(required=True)
    taxi = fields.Nested(HailTaxiSchemaContent(), required=True)


class HailSchema(Schema):
    """Validation for parameters sent by le.taxi API to request a hail.

    The parameter should be an object with the key "data" and the value a list
    of one element, the payload."""
    class Meta:
        """Allow extra fields."""
        unknown = EXCLUDE

    data = fields.List(
        fields.Nested(HailSchemaContent),
        required=True,
        validate=validate.Length(min=1, max=1)
    )


@app.route('/hail', methods=['POST'])
def hail():
    """This endpoint is called by the API of le.taxi when one of the operator's
    taxis receives a hail.

    le.taxi assumes the operator handled the request successfully if this
    endpoint returns a HTTP/200 status code.

    After le.taxi gets the response, you have 10 seconds to call PUT
    https://api.taxi/hails/:hail_id with the status "received_by_taxi" to
    inform when the taxi receives the hail, and 30 seconds to call the same
    endpoint with:

    - {"status": "accepted_by_taxi", "taxi_phone_number": "..."} if the taxi
      accepts the hail.
    - {"status": "declined_by_taxi"} if the taxi refuses the hail.

    Refer to https://api.taxi/documentation for more detailed documentation.
    """
    errors = HailSchema().validate(request.json)
    if errors:
        return jsonify({'errors': errors}), 400

    data = request.json['data'][0]

    customer_lon = data['customer_lon']
    customer_lat = data['customer_lat']
    customer_address = data['customer_address']
    customer_phone_number = data['customer_phone_number']

    hail_id = data['id']
    taxi_id = data['taxi']['id']

    # Asynchronously notify taxi of the new hail.
    notify_taxi.queue(
        taxi_id, hail_id,
        customer_lon, customer_lat,
        customer_address,
        customer_phone_number
    )

    # Return an empty HTTP/200 response to inform the caller the query has been
    # handled.
    return jsonify({})


class AnswerSchema(Schema):
    status = fields.String(
        required=True,
        validate=validate.OneOf(['accept', 'decline'])
    )


@app.route('/answer/<taxi_id>/<hail_id>', methods=['POST'])
def answer(taxi_id, hail_id):
    """This endpoint is called by the taxi application to accept or refuse a
    hail request.  If the status is 'accept', we call le.taxi API to set the
    hail status to 'accepted_by_taxi', otherwise to 'declined_by_taxi'."""
    errors = AnswerSchema().validate(request.json)
    if errors:
        return jsonify({'errors': errors}), 400

    status = request.json['status']

    # For security reasons, we should make sure taxi_id and hail_id are
    # correct.

    # The special hail status "accepted_by_taxi" requries to provide the taxi
    # phone number.
    if status == 'accept':
        update_hail.queue(hail_id, 'accepted_by_taxi',
                          taxi_phone_number='0607080910')
    else:
        update_hail.queue(hail_id, 'declined_by_taxi')

    return jsonify({})
