import os

DEBUG = True

TEMPLATE_DEBUG = DEBUG

MANAGERS = (
    
)

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'

DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'griffoncms',
        'USER': 'postgres',
        'PASSWORD' : 'root',
        'HOST' : 'localhost',
   }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# GROUP_NAME is used by the caching structure to cache elements across multiple sites. All sites with a common GROUP_NAME will share cache.
GROUP_NAME = 'griffoncms'
# GROUP_CACHE_VERSION can be incremented/changed to break cache across all sites in a group.
GROUP_CACHE_VERSION = 1

# Multiple site settings.
SITE_ID = 1
SITE_DOMAIN = '127.0.0.1:8000'
# SITE_PREFIX is used to cache things in a site-specific way.
SITE_PREFIX = 'griffon_com'

# Used as the from address for most emails.
SITE_FROM_EMAIL = 'webmaster@griffoncms.com'
# Default state displayed when registering.
DEFAULT_STATE = ('MA', 'Massachusetts')

SESSION_COOKIE_DOMAIN = None

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "site-media")
MEDIA_DOMAIN = '127.0.0.1:8000'
MEDIA_URL = MEDIA_DOMAIN + '/'+SITE_PREFIX+'/'

SECRET_KEY = '=u0x6&mz9k=tu+!m$=h_-s6u0-xn+yuvqvd)t^ujn+zrsrj9g^'

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # app default templates load from the app template folder using the
    # app_directories template loader
    # must be structured as <app_name>/templates/<app_name>/template.html

    # site specific templates
    os.path.join(os.path.dirname(__file__), "templates"),
    
    # cluster specific templates
    os.path.join(os.path.dirname(__file__), "../../common_templates"),

    # cms default templates
    os.path.join(os.path.dirname(__file__), "../../../../common_templates"),
)


# site cache key prefix
CACHE_MIDDLEWARE_KEY_PREFIX = SITE_PREFIX
# Incrementing or changing cache version breaks site-specific cache.
CACHE_VERSION = 1
# Whether or not to cache the rendered HTML of content pages.
CACHE_HTML = None

# eprise cache default settings
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHE_MIDDLEWARE_SECONDS = 60 * 3 # 3 minutes
CACHE_LONG_SECONDS = 60 * 60 * 24 * 14 # 2 weeks max memcache

SESSION_SAVE_EVERY_REQUEST = False

# eprise middleware
# middleware may not be added to anywhere else for CMS sites
# middleware may be overridden at cluster or site level if needed
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',


)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    )


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.i18n',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)


USE_I18N = False

INSTALLED_APPS = (
    # DJANGO INCLUDES
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages', 
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.redirects',
    'django.contrib.staticfiles',
    
    # EXTERNAL DEPENDENCIES
    'reversion',
    'treebeard',
    
    # CMS APPS
    'apps.categories',
    'apps.content',
    'apps.contentinfo',
    'apps.utilities',
    'apps.media_library',
    #'apps.utilities.managers'
    

    
)



INTERNAL_IPS = ('1.2.3.4',)

STATIC_ROOT = 'static/'
STATIC_URL = 'http://33.33.33.10:8000/static/'

DEBUG = True
FILE_UPLOAD_PERMISSIONS = 0775



try:
    from settings.local import *
except ImportError:
    pass
