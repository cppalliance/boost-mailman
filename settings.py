# -*- coding: utf-8 -*-
# Mailman Web configuration file.
# /etc/mailman3/settings.py

from mailman_web.settings.base import *
from mailman_web.settings.mailman import *
import os
import environs
import ast

env = environs.Env()
env.read_env()

#: Default list of admins who receive the emails from error logging.
ADMINS = ((env("ADMIN_NAME", None), env("ADMIN_EMAIL", None)),)

# Postgresql database setup.
DATABASES = {
    "default": {
        "ENGINE": env("DATABASES_DEFAULT_ENGINE", None),
        "HOST": env("DATABASES_DEFAULT_HOST", None),
        "NAME": env("DATABASES_DEFAULT_NAME", None),
        "PASSWORD": env("DATABASES_DEFAULT_PASSWORD", None),
        "PORT": env("DATABASES_DEFAULT_PORT", None),
        "USER": env("DATABASES_DEFAULT_USER", None),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# 'collectstatic' command will copy all the static files here.
# Alias this location from your webserver to `/static`
STATIC_ROOT = env("STATIC_ROOT")

# enable the 'compress' command.
COMPRESS_ENABLED = True

if env("WEB_LOG_FILE", None):
    # Make sure that this directory is created or Django will fail on start.
    LOGGING["handlers"]["file"]["filename"] = env("WEB_LOG_FILE")
else:
    #: Logging configuration.
    del LOGGING["handlers"]["file"]
    LOGGING["handlers"]["console"]["level"] = "INFO"
    LOGGING["formatters"]["simple"]["format"] = "%(levelname)s %(name)s %(message)s"
    # In case the handler config is updated upstream, we don't want to fully overwrite it, so we just manipulate it
    for _logger in LOGGING["loggers"].values():
        _handlers = _logger["handlers"]
        for _handler in ("file", "mail_admins"):
            try:
                _handlers.remove(_handler)
            except ValueError:
                pass
        if "console" not in _handlers:
            _logger["handlers"].append("console")

#: Hosts/domain names that are valid for this site; required if DEBUG is False.
#: See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]  # Archiving API from Mailman, keep it.
ALLOWED_HOSTS.extend(env("ALLOWED_HOSTS", None).split(", "))

if env("DJANGO_URLS_MODULE_NAME", None):
    #: URL Configuration for Django
    ROOT_URLCONF = env("DJANGO_URLS_MODULE_NAME")

#: See https://docs.djangoproject.com/en/dev/ref/settings/#csrf-trusted-origins
#: For Django <4.0 these are of the form 'lists.example.com' or
#: '.example.com' to include subdomains and for Django >=4.0 they include
#: the scheme as in 'https://lists.example.com' or 'https://*.example.com'.
CSRF_TRUSTED_ORIGINS = []
# "lists.your-domain.org",
# Add here all production domains you have.
CSRF_TRUSTED_ORIGINS.extend(env("CSRF_TRUSTED_ORIGINS", None).split(", "))

#: Current Django Site being served. This is used to customize the web host
#: being used to serve the current website. For more details about Django
#: site, see: https://docs.djangoproject.com/en/dev/ref/contrib/sites/
SITE_ID = int(env("SITE_ID", 1))

# Set this to a new secret value.
SECRET_KEY = env("SECRET_KEY", None)

# Set this to match the api_key setting in
# /opt/mailman/mm/mailman-hyperkitty.cfg (quoted here, not there).
MAILMAN_ARCHIVER_KEY = env("MAILMAN_ARCHIVER_KEY", None)
if env.bool("MAILMAN_ARCHIVER_FROM", None):
    MAILMAN_ARCHIVER_FROM = env("MAILMAN_ARCHIVER_FROM", None)

# The sender of emails from Django such as address confirmation requests.
# Set this to a valid email address.
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", None)

# The sender of error messages from Django. Set this to a valid email
# address.
SERVER_EMAIL = env("SERVER_EMAIL", None)

# Mailman API credentials
MAILMAN_REST_API_URL = env("MAILMAN_REST_API_URL", None)
MAILMAN_REST_API_USER = env("MAILMAN_REST_API_USER", None)
MAILMAN_REST_API_PASS = env("MAILMAN_REST_API_PASS", None)
if env.bool("MAILMAN3_USE_PYSASSC", False):
    #: django-compressor
    #: https://pypi.python.org/pypi/django_compressor
    COMPRESS_PRECOMPILERS = (
        ("text/x-scss", "pysassc -t compressed {infile} {outfile}"),
        ("text/x-sass", "pysassc -t compressed {infile} {outfile}"),
    )

if env("DJANGO_DEBUG", None) == "True":
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    # When DEBUG is True, don't actually send emails to the SMTP server, just store
    # them in a directory. This way you won't accidentally spam your mailing-lists
    # while you're fiddling with the code.
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = os.path.join(env("WEB_VAR_DIR", None), "emails")

if env("HAYSTACK_ENGINE", None):
    #
    # Full-text search engine
    #
    if env("HAYSTACK_ENGINE_ELASTIC", None) == "True":
        HAYSTACK_CONNECTIONS = {
            "default": {
                "ENGINE": env("HAYSTACK_ENGINE", None),
                "URL": env("ELASTICSEARCH_URL", None),
                "INDEX_NAME": env("ELASTICSEARCH_INDEX_NAME", None),
            },
        }
    else:
        HAYSTACK_CONNECTIONS = {
            "default": {
                "ENGINE": env("HAYSTACK_ENGINE", None),
                "PATH": os.path.join(env("WEB_VAR_DIR", None), "fulltext_index"),
            },
        }

if env("SOCIALACCOUNT_PROVIDERS", None):
    for provider in env("SOCIALACCOUNT_PROVIDERS", None).split(", "):
        provider = provider.strip()
        INSTALLED_APPS.append("allauth.socialaccount.providers.%" % provider)

if env("USE_X_FORWARDED_HOST", None):
    # If you're behind a proxy, use the X-Forwarded-Host header
    # See https://docs.djangoproject.com/en/1.8/ref/settings/#use-x-forwarded-host
    USE_X_FORWARDED_HOST = env.bool("USE_X_FORWARDED_HOST", False)

if env("SECURE_PROXY_SSL_HEADER", None):
    # And if your proxy does your SSL encoding for you, set SECURE_PROXY_SSL_HEADER
    # https://docs.djangoproject.com/en/1.8/ref/settings/#secure-proxy-ssl-header
    SECURE_PROXY_SSL_HEADER = env("SECURE_PROXY_SSL_HEADER", "https")

if env("LANGUAGE_CODE", None):
    # Internationalization
    # https://docs.djangoproject.com/en/1.8/topics/i18n/
    LANGUAGE_CODE = env("LANGUAGE_CODE", None)

if env("TIME_ZONE", None):
    TIME_ZONE = env("TIME_ZONE", None)

if env("DEFAULT_HTTP_PROTOCOL", None):
    # Django Allauth
    # You probably want https in production
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = env("DEFAULT_HTTP_PROTOCOL", None)

if env("SOCIALACCOUNT_PROVIDERS", None):
    SOCIALACCOUNT_PROVIDERS = {}
    for provider in env("SOCIALACCOUNT_PROVIDERS", None).split(", "):
        provider = provider.strip()
        variablename = "SOCIALACCOUNT_PROVIDERS_%" % provider.upper()
        SOCIALACCOUNT_PROVIDERS.update({provider, ast.literal_eval(env(variablename, None))})

if env("COMPRESS_OFFLINE", None):
    #
    # django-compressor
    # https://pypi.python.org/pypi/django_compressor
    #
    # On a production setup, setting COMPRESS_OFFLINE to True will bring a
    # significant performance improvement, as CSS files will not need to be
    # recompiled on each requests. It means running an additional "compress"
    # management command after each code upgrade.
    # http://django-compressor.readthedocs.io/en/latest/usage/#offline-compression
    COMPRESS_OFFLINE = env.bool("COMPRESS_OFFLINE", None)

if env("HYPERKITTY_ATTACHMENT_FOLDER", None):
    HYPERKITTY_ATTACHMENT_FOLDER = env("HYPERKITTY_ATTACHMENT_FOLDER", None)

if env("ADD_REMOTE_ADDR_MIDDLEWARE", None):
    # Add custom middleware to set REMOTE_ADDR when using a unix domain socket
    MIDDLEWARE = MIDDLEWARE + (env("ADD_REMOTE_ADDR_MIDDLEWARE", None),)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2024-09. Temporarily removing customizations. Can be returned later.

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static_custom')
# ]
#
TEMPLATES[0]['DIRS'] = [
    os.path.join(BASE_DIR, 'templates')
]
