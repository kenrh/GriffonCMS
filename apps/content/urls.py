from django.conf.urls import url, patterns
        
info_dict = {
    'date_field': 'publish_at',
    'allow_empty': False,
}


urlpatterns = patterns('',

    #MAIN CONTENT
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[\w-]+)-(?P<content_type>\w{2})-(?P<id>\d{1,10})/$', 'apps.content.views.content_display', name="content_detail"),
)
