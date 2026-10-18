#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
if [ "${CREATE_PRODUCTION_ADMIN_ONCE:-false}" = "true" ]; then
    python manage.py ensure_production_admin
fi