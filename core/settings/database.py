import os

from .base import BASE_DIR

DATABASE = os.getenv('DATABASE', 'sqlite')

if DATABASE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif DATABASE == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
            'NAME': os.environ.get('DB_NAME', 'postgres'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        },
    }
else:
    assert False, 'Не указан тип БД в .env Файле. sqlite or postgres'
