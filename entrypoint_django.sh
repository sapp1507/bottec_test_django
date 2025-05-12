#!/bin/bash

python manage.py makemigrations
python manage.py migrate
yes yes | python manage.py collectstatic && daphne -b 0.0.0.0 core.asgi:application --port 8000
