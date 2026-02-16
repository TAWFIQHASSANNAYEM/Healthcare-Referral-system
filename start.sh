#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --verbosity 2

echo "Starting gunicorn..."
gunicorn backend.wsgi --log-file -
