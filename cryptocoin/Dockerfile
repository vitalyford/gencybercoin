FROM python:3.7-slim

WORKDIR /code

COPY . /code/

RUN python -m pip install --upgrade pip

RUN python -m pip install -r /code/requirements.txt
RUN python manage.py collectstatic --noinput
