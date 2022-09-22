FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install git -y
RUN pip3 install --upgrade pip
RUN pip3 install --ignore-requires-python -r requirements.txt

COPY /src .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD gunicorn --workers 1 --timeout 90 --log-level=debug --bind $DJANGO_HOST:$DJANGO_PORT settings.wsgi:application