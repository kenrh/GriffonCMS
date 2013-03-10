from django.conf.urls import patterns, url


urlpatterns = patterns('',
    #url(r'^image/(?P<width>[\d-]+)/(?P<height>[\d-]+)/(?P<id>\d{1,10})/(?P<slug>[\w-]+)/$', 'media_library.views.image_view', name="image_view"),
    #url(r'^image/(?P<width>[\d-]+)/(?P<height>[\d-]+)/$', 'media_library.views.remote_image_view', name="remote_image_view"),
    #url(r'^image/full/(?P<id>\d{1,10})/(?P<slug>[\w-]+)/$', 'media_library.views.image_full_view', name="image_full_view"),
    #url(r'^file/(?P<id>\d{1,10})/(?P<slug>[\w-]+)/$', 'media_library.views.file_view', name="file_view"),
)
