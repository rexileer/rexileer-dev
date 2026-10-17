#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py sync_portfolio_registry
python manage.py prune_analytics || echo "Analytics cleanup deferred to daily timer" >&2
exec gunicorn -b 0.0.0.0:8080 portfolio.wsgi:application
