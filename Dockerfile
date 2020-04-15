FROM python:3

ENV FLASK_APP=minimal_operateur_server.api

COPY . /app

WORKDIR /app

RUN pip3 install .

RUN useradd api
USER api
