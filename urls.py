from django.conf.urls import *
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^gfmedia/', include('apps.media_library.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^static/(.*)$', 'django.views.static.serve', kwargs={'document_root': 'static'}),
    url(r'^', include('apps.content.urls')),
    
)

urlpatterns += staticfiles_urlpatterns()