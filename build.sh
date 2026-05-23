#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Collect static files (важно делать это ПОСЛЕ установки зависимостей)
python manage.py collectstatic --no-input