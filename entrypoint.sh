#!/bin/bash

set -e

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - executing migrations"
python manage.py migrate --noinput

echo "Creating superuser if it doesn't exist"
python manage.py shell << PYTHON
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin/admin')
else:
    print('Superuser already exists')
PYTHON

echo "Starting Django development server"
exec python manage.py runserver 0.0.0.0:8000
