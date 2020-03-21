import os, json

DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRET_KEY = 'hbher#51l9s0zg95-0vg^lvbvwpi!=hp)*5rs7c=favo^w_202'
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'drf_yasg',
    'import_export',
    'django_s3_storage',
    'rest_framework',
    'rest_framework.authtoken',
    'livesync',
    'sslserver',
    'corsheaders',
    'django_crontab',
]
DJANGO_LIVESYNC = {
    'PORT': 8000 # this is optional and is default set to 9001.
}


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'livesync.core.middleware.DjangoLiveSyncMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'app')],
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

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}
REDOC_SETTINGS = {
   'LAZY_RENDERING': False,
}



CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True


WSGI_APPLICATION = 'api.settings.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

ROOT_DIR = os.path.dirname(BASE_DIR)
print(ROOT_DIR)
STATIC_URL="/mnt/c/venduster/staging/.static_root/"
STATIC_DIR = '/mnt/c/venduster/staging/.static_root'
STATICFILES_DIRS = [
    STATIC_DIR,
]
STATIC_ROOT = '/mnt/c/venduster/staging/static_root'
print()

import pymysql
pymysql.install_as_MySQLdb()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ansana',
        'USER': 'venduster',
        'PASSWORD': 'Qpsej0424!',
        'HOST': 'ansana.c2j2y3bckthb.ap-northeast-2.rds.amazonaws.com',
        'PORT': '3306'
    }

}