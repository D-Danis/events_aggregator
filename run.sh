#!/bin/bash
set -e 

uv run python manage.py migrate --noinput

# Собираем статические файлы
# uv run python manage.py collectstatic --noinput

uv run gunicorn -b 0.0.0.0:8000 \
    --workers=1 \
    --threads=8 \
    --worker-class=gthread \
    --timeout 120 \
    src.core.wsgi:application