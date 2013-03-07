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
        'USER': 'pguser',
        'PASSWORD' : 'root',
        'HOST' : 'localhost',
   }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SITE_ID = 1
SITE_DOMAIN = '127.0.0.1:8000'
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

#ROOT_URLCONF = 'cms.clusters.fl.sites.centrotampa_com.urls'

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
CACHE_VERSION = 1

# eprise cache default settings
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHE_MIDDLEWARE_SECONDS = 60 * 3 # 3 minutes
CACHE_LONG_SECONDS = 60 * 60 * 24 * 14 # 2 weeks max memcache
CACHE_SEARCH_RSS_SECONDS = 60 * 60 # in search, cache an RSS feed for 1 hour
CACHE_MIDDLEWARE_KEY_PREFIX = ''
CACHE_VERSION = 1
CACHE_HTML = None
CACHE_PAGEMANAGER_SECONDS = 240

CDN_CACHE_TIMEOUT = 240

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

# eprise template loaders
# template loaders may not be added to anywhere else for CMS sites
# template loaders may be overridden at cluster or site level if needed
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)


USE_I18N = False

ADMINS = (
    ('dukecms2', 'dukecms2@gmail.com'),
)

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
    
    # EXTERNAL DEPENDENCIES
    'reversion',
    'treebeard',
    
    # CMS APPS
    'apps.categories',
    'apps.content',
    'apps.utilities'
    

    
)



INTERNAL_IPS = ('1.2.3.4',)


DEBUG = True
FILE_UPLOAD_PERMISSIONS = 0775

CLUSTER_PREFIX = None
SITE_PREFIX = None



try:
    from settings.local import *
except ImportError:
    pass
