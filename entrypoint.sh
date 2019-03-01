#!/bin/bash
mkdir -p LOG_DIR
touch $ERROR_LOG
crond
python manage.py collectstatic --noinput
python manage.py crontab add
exec "$@"
