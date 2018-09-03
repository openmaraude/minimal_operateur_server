FROM python:2.7.15-alpine3.6

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install gunicorn
