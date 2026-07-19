"""
Django settings for presence project.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

# Build paths inside the project like this: BASE_DIR / "subdir"
from pathlib import Path

from hlcs.gates import HpccExternal, HpccInternal


BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# TODO: spostare SECRET_KEY, DEBUG e ALLOWED_HOSTS su variabili d'ambiente
SECRET_KEY = "d((ew0%@e^l1*inklo4wb%iuirnq&&f#kp^#g-ve+n4t=x%%f*"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "gatecontrol",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

SERIALIZATION_MODULES = {"yml": "django.core.serializers.pyyaml"}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    )
}

ROOT_URLCONF = "presence.urls"

WSGI_APPLICATION = "presence.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "ATOMIC_REQUESTS": True,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "it-it"

TIME_ZONE = "Europe/Rome"

USE_I18N = True

# il db di produzione contiene datetime in ora locale
# (Europe/Rome) e l'app è mono-timezone; passare a True richiede una
# migrazione delle date già presenti
USE_TZ = False

# di default ora viene settato 'BigAutoField' (64 bit) però si deve cambiare pure nel db
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# Autenticazione
# https://docs.djangoproject.com/en/5.2/ref/settings/#login-redirect-url

# senza questi Django redirige al default /accounts/profile/ (non routato → 404)
# e il logout renderizza il template logged_out dell'admin
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

# destinazione di collectstatic in produzione (non è la sorgente static/)
STATIC_ROOT = BASE_DIR / "staticfiles"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "presence.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(thread)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "loggers": {
        "gatecontrol": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "hlcs": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


GATES = {
    "internal": HpccInternal(),
    "external": HpccExternal(),
}


try:
    from .local_settings import *  # noqa: F403
except ImportError:
    pass
