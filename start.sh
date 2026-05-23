#!/usr/bin/env bash
set -o errexit

# Apply migrations if needed
python manage.py migrate --no-input

# Start Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT showsystem.wsgi:application