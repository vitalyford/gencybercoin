#!/bin/bash

# bring the stuff down just in case if it has not been down yet
docker-compose down

echo Building and running the containers...
docker-compose up -d --build

echo Waiting for 15 sec for postgres database to start up...
docker-compose exec postgres sleep 15

echo Creating postgres user...
docker-compose exec postgres psql -U postgres -c "CREATE USER coin_admin PASSWORD 'go-figure-me-cow'"
echo If you see an ERROR here, no big deal

echo Creating postgres DB...
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE coin_db OWNER coin_admin"
echo If you see an ERROR here, no big deal

echo Making migrations...
docker-compose exec web python manage.py makemigrations --noinput

echo Migrating to the database...
docker-compose exec web python manage.py migrate --noinput

echo Setting up defaults...
docker-compose exec web python manage.py setdefaults

echo Collecting static files like Javascript, CSS, background image, etc...
docker-compose exec web python manage.py collectstatic --noinput

echo Done! The server should be running on your IP address, port 80
