# Example of uwsgi.ini to mount in /uwsgi.ini:
#
# [uwsgi]
#
# master = true
# processes = 2
# plugin = python3
# module = minimal_operateur_server.api
# socket = 0.0.0.0:5001
# stats = 0.0.0.0:5008 --stats-http

FROM ubuntu

RUN apt-get update && apt-get install -y \
  python3-pip \
  uwsgi \
  uwsgi-plugin-python3

ENV LC_ALL=C.UTF-8

RUN useradd api

COPY . /app
WORKDIR /app

RUN pip3 install .

USER api

CMD ["uwsgi", "/uwsgi.ini"]
