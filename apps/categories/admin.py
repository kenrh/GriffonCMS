from django.contrib import admin

from treebeard.admin import TreeAdmin
from apps.categories.models import Category

class CategoryAdmin(TreeAdmin):
    # TODO: The TreeAdmin thing is pretty much awful usability wise. It needs to be redone.
    change_list_template = "admin/change_list.html"
    
admin.site.register(Category, CategoryAdmin)