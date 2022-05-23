import os


RQ_REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

API_TAXI_URL = os.getenv('API_TAXI_URL', 'https://dev.api.taxi')

# le.taxi API key, required to change the hail status.
API_TAXI_KEY = os.getenv('API_TAXI_KEY')
