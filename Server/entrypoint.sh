#!/bin/bash

# Wait for PostgreSQL
until pg_isready -h db -U postgres; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create staticfiles directory if missing
mkdir -p staticfiles

# Collect static files
python manage.py collectstatic --noinput

exec "$@"
