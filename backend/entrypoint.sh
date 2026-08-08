#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py sync_portfolio_registry
exec gunicorn -b 0.0.0.0:8080 portfolio.wsgi:application
