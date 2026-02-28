#!/bin/sh
set -e
python manage.py migrate --noinput
exec gunicorn -b 0.0.0.0:8080 portfolio.wsgi:application
