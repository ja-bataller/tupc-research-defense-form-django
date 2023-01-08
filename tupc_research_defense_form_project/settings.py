"""
Django settings for tupc_research_defense_form_project project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5+w!z$k!ik+v8=$0lc#=l1awb)&!ko6g@b(f#8o13t7pvc9&5f'

# SECURITY WARNING: don't run with debug turned on in production!
# Comment when deployed
DEBUG = True
ALLOWED_HOSTS = []

# Uncomment when deployed
# DEBUG = False
# ALLOWED_HOSTS = ['www.ditresearchdefense.online ']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'tupc_research_defense_form_web_app.apps.TupcResearchDefenseFormWebAppConfig',
]

AUTH_USER_MODEL = 'tupc_research_defense_form_web_app.User'

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

ROOT_URLCONF = 'tupc_research_defense_form_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        # 'DIRS':  [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'tupc_research_defense_form_project.wsgi.application'

# Uncomment when Deployed
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'unofficialtupcre$tupc_research_defense_form_db',
#         'HOST': 'unofficialtupcresearchdefense.mysql.pythonanywhere-services.com',
#         'USER': 'unofficialtupcre',
#         'PASSWORD': '!!!tupc!!!',
#     }
# }

# Comment when Deployed
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tupc_research_defense_form_db',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': '',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# STATIC_ROOT = '/home/johnanthonybataller/tupc-research-defense-form-django/static'

MEDIA_URL = 'uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uhsG1tCRrm3fUHcG4dyEMDDq31WQULMNJkSGQFq0oiV5vvhui9')



# Email Settings
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = "unofficial.tupc.uitc@gmail.com"
EMAIL_HOST_PASSWORD = "pyuhbqjiwogsvdtp"
EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
