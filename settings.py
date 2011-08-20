import os

PRODUCTION = False

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

LOGIN_URL = '/accounts/signin/'

LOG_FILE = 'logging.log'

ADMINS = ( ('Clay Woolam', 'clay@coclass.com'), )
MANAGERS = ADMINS

if PRODUCTION:
    DEBUG = False
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'coclass',
            'USER': 'coclass',
            'PASSWORD': '',
            'HOST': '127.0.0.1',
            'PORT': '5432',      
        }
    }
    MEDIA_ROOT = os.path.join(SITE_ROOT, '/media/static/')
    CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
else:
    DEBUG = True
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    MEDIA_ROOT = os.path.join(SITE_ROOT, '/media/static/')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'coclassdev',
            'USER': 'coclass',
            'PASSWORD': 'coclass',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

HAYSTACK_SITECONF = 'search_sites'
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr'

SITE_ID = 1

USE_I18N = True


MEDIA_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

SECRET_KEY = ''

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = ( os.path.join(SITE_ROOT, 'template/'),)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_extensions',
    'logicaldelete',
    'oembed',
    'haystack',
    'django_messages',
    'timezones',
    'sorl.thumbnail',
    'classes',
    'places',
    'accounts',
    'search',
    'host',
    'invite',
    'socialauth',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django_messages.context_processors.inbox",
)

AUTH_PROFILE_MODULE = 'accounts.UserProfile'

AUTHENTICATION_BACKENDS = ( 'accounts.backend.EmailBackend', 
        'socialauth.auth_backends.FacebookBackend', )

GOOGLE_API_KEY = ''
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

FACEBOOK_APP_ID = ''
FACEBOOK_API_KEY = ''
FACEBOOK_SECRET_KEY = ''

ADD_LOGIN_REDIRECT_URL = '/accounts/signin/'
LOGIN_REDIRECT_URL = '/accounts/signin/'

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
