"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import datetime
import os

from django.conf import settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from mysite.router import DatabaseAppsRouter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%ur^wgur*+1c$kxk_(bkqonaebu3&f#a7v+g7j)65k=6%z*itz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']

# my settings
# easy_thumbnails settings
THUMBNAIL_HIGH_RESOLUTION = True
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'easy_thumbnails.processors.scale_and_crop',
    'easy_thumbnails.processors.filters',
)
THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (160, 90), 'crop': True},
        'big_avatar': {'size': (800, 450), 'crop': True},
    },
}
THUMBNAIL_BASEDIR = 'thumbs'

# Application definition
INSTALLED_APPS = [
    'easy_thumbnails',
    'admin_resumable',
    "djangocms_admin_style",
    'django.contrib.admin',
    'django.contrib.auth',
    # 'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # user apps
    'corsheaders',
    'vodmanagement.apps.VodConfig',
    'epg.apps.EpgConfig',
    'rest_framework',
    'django_crontab',

    # Sorted Many to Many Field
    'sortedm2m',
    # 'rest_framework_docs',
    # 'drf_autodocs'
    # 'rest_framework_swagger',

    # Scheduler App
    # 'django_celery_beat',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'mysite.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'mysite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASE_ROUTERS = ['mysite.router.DatabaseAppsRouter']
DATABASE_APPS_MAPPING = {
    'epg': 'tsrtmp'
}
DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.mysql',
        'NAME' : 'vod',
        'USER' : 'root',
        'PASSWORD': '123',
        'HOST': os.getenv('DJANGO_DB_HOST', ''),
        'PORT': '',#'3306',
    },
    'tsrtmp': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tsrtmp',
        'USER': 'root',
        'PASSWORD': '123',
        'HOST': os.getenv('TSRTMP_DB_HOST', os.getenv('DJANGO_DB_HOST', '')),
        'PORT': '',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
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

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        'rest_framework.permissions.IsAuthenticated',
    )
}

CRONJOBS = [
    ('25 19 * * *', 'epg.cron.get_program'),
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = 'zh-Hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
# Django Admin 和 Django其他应用中的静态文件默认存储位置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Django中第三方文件存储文件位置，Django能且只能访问该目录下的文件
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 电视回看节目.m3u8和.ts文件的转储文件夹
RECORD_MEDIA_FOLDER = 'record'
RECORD_MEDIA_ROOT = os.path.join(MEDIA_ROOT, RECORD_MEDIA_FOLDER)

# 本地上传文件存储位置，支持直接通过文件系统拷贝到该目录下，然后在管理页面上直接选择该目录下的文件
LOCAL_FOLDER_NAME = 'local_file'
LOCAL_MEDIA_URL = LOCAL_FOLDER_NAME + '/'
LOCAL_MEDIA_ROOT = os.path.join(MEDIA_ROOT, LOCAL_FOLDER_NAME)

# admin_resumable 配置
ADMIN_RESUMABLE_CHUNKSIZE = 1024 * 1024 * 10
ADMIN_RESUMABLE_STORAGE = 'vodmanagement.my_storage.VodStorage'
ADMIN_RESUMABLE_SHOW_THUMB = True

SYSTEM_MEDIA_ROOT = '/media/tongshi'
DEFAULT_IMAGE_SRC = STATIC_URL + 'missing.jpg'

# Memory Cache
CACHES = {
    'default':{
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Scheduler App
CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
