FROM python:3.7-slim

WORKDIR /code

RUN python -m pip install --upgrade pip

COPY . /code/

RUN python -m pip install -r /code/requirements.txt
