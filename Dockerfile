FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app
COPY site /app/site

ENV DJANGO_SETTINGS_MODULE=portfolio.settings
RUN python manage.py migrate --noinput
RUN python manage.py load_initial_data || true

EXPOSE 8080
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
