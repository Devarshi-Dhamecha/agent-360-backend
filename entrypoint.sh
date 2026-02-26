#!/bin/sh

echo "Waiting for database..."

# Optional: add wait-for-db logic if needed

echo "Collecting static..."
python manage.py collectstatic --noinput

#echo "Running migrations..."
#python manage.py migrate --noinput

echo "Starting Gunicorn App..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 2