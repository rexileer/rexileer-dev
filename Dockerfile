FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app
COPY site /app/site

ENV DJANGO_SETTINGS_MODULE=portfolio.settings
# Build-only random keys stay in process memory, never in an image ENV or file.
RUN python -c "import os, secrets; os.environ['DJANGO_SECRET_KEY'] = secrets.token_urlsafe(64); os.environ['DJANGO_SETTINGS_MODULE'] = 'portfolio.settings'; import django; django.setup(); from django.core.management import call_command; call_command('migrate', interactive=False); call_command('collectstatic', interactive=False, clear=True)"
RUN python -c "import os, secrets; os.environ['DJANGO_SECRET_KEY'] = secrets.token_urlsafe(64); os.environ['DJANGO_SETTINGS_MODULE'] = 'portfolio.settings'; import django; django.setup(); from django.core.management import call_command; call_command('load_initial_data')" || true

EXPOSE 8080
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
