#!/bin/sh
set -e
if [ "${DJANGO_SETTINGS_MODULE:-}" = "desk_config.settings" ]; then
  umask 077
  mkdir -p /app/desk-db /app/desk-documents
  python manage.py migrate --noinput
  python manage.py desk_owner --generate-file /run/desk-bootstrap/owner-password.txt
  chown -R 10001:10001 /app/desk-db
  chown -R 10001:10001 /app/desk-documents
  chmod 700 /app/desk-db
  chmod 700 /app/desk-documents
  exec gunicorn -b 0.0.0.0:8080 --workers 1 --threads 2 --user 10001 --group 10001 --timeout 30 --max-requests 500 --max-requests-jitter 50 --access-logfile /dev/null desk_config.wsgi:application
fi
python manage.py migrate --noinput
python manage.py sync_portfolio_registry
python manage.py prune_analytics || echo "Analytics cleanup deferred to daily timer" >&2
exec gunicorn -b 0.0.0.0:8080 portfolio.wsgi:application
