import os
from pathlib import Path
import logging
import yaml
from django.apps import AppConfig
import django_heroku
from django.core.checks import database
import dj_database_url
import whitenoise

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = Path(__file__).resolve().parent.parent



with open(os.path.join(
       os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yml'), "r") as f:
    RAW_CONFIG = yaml.safe_load(f)
    secret_key = RAW_CONFIG['django']['secret_key']
    current_db = RAW_CONFIG['database']['db']
    db_config = RAW_CONFIG[current_db]



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret_key

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = bool(os.getenv("DEBUG",True))

logging.basicConfig(level=logging.DEBUG, filename='GT.log', format='%(name)s - %(levelname)s - %(message)s')
logging.debug('This will get logged')

ALLOWED_HOSTS = ['*']
FILE_UPLOAD_MAX_MEMORY_SIZE = 20621440
DATA_UPLOAD_MAX_MEMORY_SIZE = 20621440
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gtree_db',
    'Co_vision',
    'rest_framework',
    'API',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'Gen_tree.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'Gen_tree.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': db_config['database'],
        'USER' : db_config['user'],
        'PASSWORD' : db_config['password'],
        'HOST' : db_config['host'],
        'PORT' : db_config['port'],
        'default-character-set': 'utf8'
    }
}
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru'
DATE_FORMAT = '%d/%m/%Y'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
#STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), os.path.join(BASE_DIR, 'media'))

STATIC_URL = '/static/'
LOGIN_URL = '/login/'
MEDIA_ROOT = BASE_DIR / 'media'


MEDIA_URL = "media/"
LOGIN_REDIRECT_URL = 'login/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
django_heroku.settings(locals())