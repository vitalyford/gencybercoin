# pull official base image
FROM python:3.7-alpine

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src/cryptocoin

# install dependencies
RUN pip install --upgrade pip
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libjpeg-turbo-dev zlib-dev

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/cryptocoin/entrypoint.sh

# copy project
COPY . /usr/src/cryptocoin/

RUN pip install -r /usr/src/cryptocoin/requirements.txt

# run entrypoint.sh
ENTRYPOINT ["/usr/src/cryptocoin/entrypoint.sh"]