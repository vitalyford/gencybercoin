"""
Django settings for GenCyberCoin project.

"""

import dj_database_url #dj-database-url==0.4.1
import django_on_heroku
import os

# Static files (CSS, JavaScript, Images)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

if 'RDS_DB_NAME' in os.environ:  # if we run on AWS
    from cryptocoin.aws.conf import *
else:
    STATIC_URL = '/static/'

    # File storage settiings
    MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
    MEDIA_URL = '/media/'


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    SECRET_KEY = '(v3q0od-tzk)gi-miq+4)5qnka6)by6x37+lk=fbk$x&+20&6b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'user.apps.UserConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'storages',
]

MIDDLEWARE = [
    #'sslify.middleware.SSLifyMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cryptocoin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['../user/templates/user', 'user/templates/user'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cryptocoin.wsgi.application'

# Database
'''
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600),
}
'''
if 'RUNNING_ON_HEROKU' in os.environ:
    django_on_heroku.settings(locals())
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=500, ssl_require=True)
    }
    del DATABASES['default']['OPTIONS']['sslmode']
elif 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
elif 'RUN_IN_DOCKER' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'coin_db',
            'USER': 'coin_admin',
            'PASSWORD': 'go-figure-me-cow',
            'HOST': 'postgres',
            'PORT': '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'coin_db',
            'USER': 'coin_admin',
            'PASSWORD': 'go-figure-me-cow',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CSRF_FAILURE_VIEW = 'user.views.csrf_failure'

# Secure settings
#SSLIFY_DISABLE = True
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#X_FRAME_OPTIONS = 'Deny'
#SECURE_CONTENT_TYPE_NOSNIFF = True
#SECURE_SSL_REDIRECT = True
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
#SECURE_BROWSER_XSS_FILTER = True
#SECURE_HSTS_SECONDS = 1
#SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#SECURE_HSTS_PRELOAD = True

IMPORT_EXPORT_USE_TRANSACTIONS = True

DEFAULT_HONORARY_COINS = 50
DEFAULT_PERMANENT_COINS = 0

SESSION_EXPIRY_TIME = 21600

DATA_UPLOAD_MAX_MEMORY_SIZE = 10500000

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
