##### DEV IMAGE #####

FROM ubuntu AS devenv

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN=true

RUN apt-get update && apt-get install -y \
  python3-pip \
  redis-tools \
  sudo \
  postgresql-client

ENV LC_ALL=C.UTF-8

RUN pip3 install tox

RUN useradd api
RUN echo "api ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

ENV VIRTUAL_ENV=/venv
ENV PATH=/venv/bin/:$PATH
ENV HOME=/tmp

ENV FLASK_APP minimal_operateur_server.api:create_app
env API_SETTINGS=/settings.py
env FLASK_DEBUG=1

USER api
WORKDIR /git/minimal_operateur_server

COPY devenv/entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
CMD ["flask", "run", "--host", "0.0.0.0"]


##### PROD IMAGE #####

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

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN=true

RUN apt-get update && apt-get install -y \
  python3-pip \
  uwsgi \
  uwsgi-plugin-python3 \
  redis-tools

ENV LC_ALL=C.UTF-8

RUN pip3 install tox

RUN useradd api

ENV FLASK_APP minimal_operateur_server.api:create_app

COPY . /app
WORKDIR /app

RUN pip3 install .

USER api

CMD ["uwsgi", "/uwsgi.ini"]
