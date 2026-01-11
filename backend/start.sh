#!/bin/bash

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2
