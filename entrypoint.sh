#!/bin/bash
mkdir -p $LOG_DIR
crond
python manage.py collectstatic --noinput
python manage.py crontab add
exec "$@"
