#!/bin/bash

python manage.py makemigrations
python manage.py migrate
yes yes | python manage.py collectstatic && daphne core.asgi:application --port 8000