from minimal_operateur_server.api import app, rq


def setup_module(module):
    # Use fakeredis for worker
    app.config['RQ_CONNECTION_CLASS'] = 'fakeredis.FakeStrictRedis'

    app.config['API_TAXI_URL'] = 'https://unittests.localhost'
    app.config['API_TAXI_KEY'] = 's3cr3t_k3y'

    rq.init_app(app)
