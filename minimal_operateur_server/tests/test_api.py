import time
import unittest
from unittest.mock import MagicMock

from fakeredis import FakeStrictRedis
import pytest
import requests

from minimal_operateur_server.api import app, notify_taxi, rq, update_hail


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def queue():
    return rq.get_queue()


@pytest.fixture
def fake_time(monkeypatch):
    """Replace time.sleep with a do-nothing function."""
    fake_time = MagicMock()
    monkeypatch.setattr(time, 'sleep', fake_time)
    yield fake_time


def test_index(client):
    resp = client.get('/')
    assert resp.status_code == 200


def test_hail_400(client):
    """Verify parameters validation."""
    # No data
    resp = client.post('/hail', json={})
    assert resp.status_code == 400

    # No payload
    resp = client.post('/hail', json={'data': []})
    assert resp.status_code == 400

    # Missing parameters
    resp = client.post('/hail', json={'data': [{
        'customer_lon': 2.35
    }]})
    assert resp.status_code == 400
    assert 'customer_lon' not in resp.json['errors']['data']['0']
    assert 'customer_lat' in resp.json['errors']['data']['0']
    assert 'customer_phone_number' in resp.json['errors']['data']['0']


def test_hail_ok(client, queue):
    return
    resp = client.post('/hail', json={
        'data': [{
            'id': 'HAIL_ID',
            'taxi': {
                'id': 'TAXI_ID'
            },
            'customer_lon': 2.308440,
            'customer_lat': 48.8505,
            'customer_address': '20 Avenue de Ségur, 75007 Paris',
            'customer_phone_number': '0600000000',

            # Extra field should be accepted
            'extra_field': None
        }],
    })
    assert resp.status_code == 200
    # Check notify_taxi is called.
    assert queue.count == 1
    assert 'notify_taxi' in queue.jobs[0].func_name


def test_answer_400(client):
    resp = client.post('/answer/TAXI/HAIL', json={})
    assert resp.status_code == 400

    resp = client.post('/answer/TAXI/HAIL', json={'status': 'invalid'})
    assert resp.status_code == 400
    assert 'status' in resp.json['errors']


def test_answer_ok(client, queue):
    return
    resp = client.post('/answer/TAXI/HAIL', json={'status': 'accept'})
    assert resp.status_code == 200
    assert queue.count == 1
    job = queue.jobs[0]
    assert 'update_hail' in job.func_name
    assert job.args == ('HAIL', 'accepted_by_taxi')
    assert 'taxi_phone_number' in job.kwargs

    queue.empty()

    resp = client.post('/answer/TAXI/HAIL', json={'status': 'decline'})
    assert resp.status_code == 200
    assert queue.count == 1
    job = queue.jobs[0]
    assert 'update_hail' in job.func_name
    assert job.args == ('HAIL', 'declined_by_taxi')
    assert 'taxi_phone_number' not in job.kwargs


def test_notify_taxi(fake_time, monkeypatch, queue):
    fake_put = MagicMock()
    monkeypatch.setattr(requests, 'put', fake_put)

    notify_taxi('TAXI', 'HAIL', 2.35, 48.86, 'Addresse', '0607099999')

    # Hail is "received_by_taxi"
    fake_put.assert_called()
    # Pending task to set to "accepted_by_taxi"
    assert queue.count == 1


def test_update_hail(client, monkeypatch):
    fake_put = MagicMock()
    monkeypatch.setattr(requests, 'put', fake_put)
    update_hail('HAIL', 'accept', taxi_phone_number='0607080910')

    fake_put.assert_called_with(
        '%s/hails/HAIL' % app.config['API_TAXI_URL'],
        json={
            'data': [{
                'status': 'accept',
                'taxi_phone_number': '0607080910'
            }]
        },
        headers={
            'X-Version': '3',
            'X-Api-Key': app.config['API_TAXI_KEY']
        }
    )
