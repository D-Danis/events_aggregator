#!/bin/bash
set -e

# Применяем миграции
uv run python manage.py migrate --noinput

# Собираем статику 
# uv run python manage.py collectstatic --noinput

# Запускаем Celery worker с beat 
uv run celery -A src.core worker -P solo -B -l INFO &

# Запускаем Gunicorn
uv run gunicorn -b 0.0.0.0:8000 \
    --workers=1 \
    --threads=8 \
    --worker-class=gthread \
    --timeout 120 \
    src.core.wsgi:application &

wait