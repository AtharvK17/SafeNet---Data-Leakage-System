from pathlib import Path
import os

from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-b$(w+x_4l1_1j6508$3#d=b2-))1-*)0&c%pz#!e8+!2d1)+z-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Accounts.apps.AccountsConfig',
    'Dashboard.apps.DashboardConfig',
    'Projects.apps.ProjectsConfig',
    'Tasks.apps.TasksConfig',
    'Dataleakage.apps.DataleakageConfig',
    'Notifications.apps.NotificationsConfig',
    'DataExplorer.apps.DataexplorerConfig',

    # Third-party apps
    'django_celery_results',
    'django_celery_beat',
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

ROOT_URLCONF = 'SafeNet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'SafeNet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# your_project/settings.py

# Celery Configuration
CELERY_BROKER_URL = 'redis://127.0.0.1:6379'  # Use Redis as the broker
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'  # For result storage
CELERY_TIMEZONE = 'Asia/Kolkata'  # Set your preferred timezone

# Celery Beat configuration (if you want to use periodic tasks)
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Example periodic task (scan files every hour)
    'scan_all_files_periodically': {
        'task': 'Dataleakage.tasks.scan_all_files_async',  # The task to scan all files
        'schedule': crontab(minute='*/5'),  # This will run every 5 minutes
    },

    # Update all users' sensitivity scores periodically (for example, every hour)
    'update_all_user_sensitivity_scores_periodically': {
        'task': 'Dataleakage.tasks.update_all_user_sensitivity_scores',
        'schedule': crontab(minute='*/3'),  # This will run every 5 minutes
    },
}

# Authentication settings
LOGIN_URL = '/Accounts/login/'  # Update this to match your Accounts URLs
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'



