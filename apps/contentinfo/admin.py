from django.contrib import admin
from reversion.admin import VersionAdmin
from apps.contentinfo.models import GFContentType

######################################
# MGFCONTENT TYPE
#######################################


class GFContentTypeAdmin(VersionAdmin):
    list_display = ('full_name', 'model_name', 'short_name', )
    ordering = ['full_name', ]


admin.site.register(GFContentType, GFContentTypeAdmin)
