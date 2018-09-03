FROM python:2.7.15-alpine3.6

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5001
ENTRYPOINT ["python"]
CMD ["python api.py"]
