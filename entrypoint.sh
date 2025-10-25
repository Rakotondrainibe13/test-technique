#!/usr/bin/env sh
set -e

echo "#### Waiting for Postgres to be available ###"
# wait for postgres
for i in $(seq 1 30); do
  python - <<'PY' >/dev/null 2>&1
import sys, os
import psycopg2
try:
    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST','db'),
        port=int(os.environ.get('POSTGRES_PORT','5432')),
        user=os.environ.get('POSTGRES_USER','test_user'),
        password=os.environ.get('POSTGRES_PASSWORD','test_pass'),
        dbname=os.environ.get('POSTGRES_DB','test_db'),
        connect_timeout=1
    )
    conn.close()
except Exception:
    sys.exit(1)
sys.exit(0)
PY
  if [ $? -eq 0 ]; then
    echo "Postgres is up"
    break
  fi
  echo "Postgres not ready, sleeping 1s... ($i/30)"
  sleep 1
done

# Run migrations
echo "### Running migrations ####"
python manage.py migrate --noinput

# Create default users if they do not exist Admin, Editor, Reader
echo "#### Ensuring default users admin, Editor, Reder exist ####"
python - <<'PY'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.contrib.auth import get_user_model
from articles.models import UserProfile
User = get_user_model()
users = [
    ('admin','adminpass','admin@example.com','admin',True,True),
    ('editor','editorpass','editor@example.com','editor',False,False),
    ('reader','readerpass','reader@example.com','reader',False,False),
]
for username,password,email,role,is_super,is_staff in users:
    obj, created = User.objects.get_or_create(username=username, defaults={'email': email})
    if created:
        obj.set_password(password)
        obj.is_superuser = is_super
        obj.is_staff = is_staff
        obj.save()
    UserProfile.objects.update_or_create(user=obj, defaults={'role': role})
print('Default users ensured')
PY

# Finally execute the container CMD (gunicorn)
exec "$@"
