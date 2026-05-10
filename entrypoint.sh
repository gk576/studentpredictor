#!/bin/bash
echo "Waiting for MySQL..."
while ! python -c "
import MySQLdb
MySQLdb.connect(host='db', user='root', passwd='password', db='edupredict_db')
" 2>/dev/null; do
  echo "MySQL not ready, retrying in 3 seconds..."
  sleep 3
done
echo "MySQL is ready!"
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
