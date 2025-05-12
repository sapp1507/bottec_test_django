#!/bin/bash
echo "Start entrypoint"
import_env() {
  if [ -f .env ]; then
    echo "Import environment variables..."
    cat .env >> /etc/environment
  fi
}

printenv >> /etc/environment

apt-get update && apt-get install -y cron rsyslog
chmod 644 /etc/cron.d/config
import_env
cron && python /django/manage.py runbot