#!/bin/bash

python manage.py makemigrations
python manage.py migrate
#yes yes | python manage.py collectstatic && daphne core.asgi:application --port 8000
yes yes | python manage.py collectstatic && python manage.py runserver 0.0.0.0:8000