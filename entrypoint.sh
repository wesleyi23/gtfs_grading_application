#!/bin/sh

echo "collecting static files"
python3 manage.py collectstatic --no-input --clear

echo "launching application"
gunicorn -b 0.0.0.0:8000 gtfs_grading.wsgi:application
exec "$@"
