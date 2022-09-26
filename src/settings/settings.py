import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from envclasses import envclass, load_env

from common.utils import BaseSettings


@envclass
@dataclass
class DjangoSettings(BaseSettings):
    host: str = 'localhost'
    server_host: str = '0.0.0.0'
    port: int = 8000
    debug: int = 1
    secret_key: str = 'super-duper-secret-key'


@envclass
@dataclass
class ELKSettings(BaseSettings):
    version: str = '8.3.1'
    elastic_host: str = 'localhost'
    logstash_host: str = 'localhost'
    kibana_host: str = 'localhost'


@envclass
@dataclass
class MarketSettings(BaseSettings):
    host: str = 'https://market.csgo.com'


SERVER_SETTINGS: DjangoSettings = DjangoSettings().from_env('DJANGO')
ELK_SETTINGS: ELKSettings = ELKSettings().from_env('ELK')
MARKET_SETTINGS: MarketSettings = MarketSettings().from_env('MARKET')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Site settings
SITE_ID = 1

# Make data dir for sqlite3
DATA_DIR = BASE_DIR.parent / 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SERVER_SETTINGS.secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = SERVER_SETTINGS.debug

ALLOWED_HOSTS = [SERVER_SETTINGS.host, SERVER_SETTINGS.server_host]

# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'preferences',
    'settings',
    'daterangefilter',
    'logs',
    'steam',
    'market',
    'bot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'preferences.context_processors.preferences_cp',
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'settings.logging.formatters.LogstashJSONFormatter',
        },
        'simple': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'logstash': {
            'level': 'INFO',
            'class': 'settings.logging.handlers.StrTCPLogstashHandler',
            'formatter': 'json',
            'host': SERVER_SETTINGS.server_host,
            'port': 50000,
            'version': 1,
            'message_type': 'bot',
            'fqdn': False,
            'tags': ['bot'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logstash', 'console'],
            'level': 'ERROR',
        },
        'steam': {
            'handlers': ['logstash', 'console'],
            'level': 'DEBUG',
        },
        'bot': {
            'handlers': ['logstash', 'console'],
            'level': 'DEBUG',
        },
        'market': {
            'handlers': ['logstash', 'console'],
            'level': 'DEBUG',
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Disable TooManyFieldsSent
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Grappelli settings - https://django-grappelli.readthedocs.io/en/latest/
GRAPPELLI_ADMIN_TITLE = 'Tm-bot admin'
GRAPPELLI_CLEAN_INPUT_TYPES = False
