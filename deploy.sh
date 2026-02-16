#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser (if needed)..."
python manage.py createsuperuser --noinput || true

echo "Importing hospital data..."
python manage.py import_hospitals || echo "No hospital data to import or command failed"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Deployment complete!"
