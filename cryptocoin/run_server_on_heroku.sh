#!/bin/bash

python manage.py migrate
python manage.py setdefaults
gunicorn cryptocoin.wsgi:application --bind 0.0.0.0:$PORT
