from datetime import datetime

from django.contrib import admin
from django import forms, template
from django.db import models
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify

from reversion.admin import VersionAdmin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.admin.options import ModelAdmin as default_Model_Admin
from django.template import RequestContext
from django.conf import settings

from apps.content.models import Article
from apps.utilities.admin_actions import delete_selected, make_draft, make_public


class ArticleAdminForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ArticleAdminForm, self).__init__(*args, **kwargs)

        # If the form is being built for an instance, you need to make sure the querysets returned have the values already assigned to them.
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
        else:
            instance = None
           
    class Meta:
        model = Article

    
    class Media:
        css = {
            'all': ('/site-media/global-media/admin/css/tabs.css', '/site-media/global-media/admin/css/no-add-another.css', '/site-media/global-media/admin/css/wider-text-fields.css',)
        }
        js = (
            '/site-media/global-media/admin/js/genericcollection.js',
            '/site-media/global-media/admin/js/js-ui/jquery-1.3.2.min.js',
            '/site-media/global-media/admin/js/js-ui/ui.core.js',
            '/site-media/global-media/admin/js/js-ui/ui.sortable.js',
            '/site-media/global-media/admin/js/js-ui/menu-sort.js',
            "/site-media/global-media/admin/js/tabs.js",
            "/site-media/global-media/admin/js/tiny_mce/tiny_mce.js",
            "/site-media/global-media/admin/js/content_tinymce.js",
        )


    def clean_slug(self):
        """ Eliminates capital letters from the slug."""
        self.cleaned_data['slug'] = self.cleaned_data['slug'].lower()
        return self.cleaned_data['slug']
        
    def clean(self):
        """
            @summary: Ensures that external articles have external URLs defined, and FrequentImages assigned belong to at least one of the sites the article does.
        """
        self.cleaned_data = super(ArticleAdminForm, self).clean()
        
        if self._errors:
            return
        
        # Search for the Unicode characters for smart quotes, and replace them with regular ones.
        if 'title' in self.cleaned_data:
            self.cleaned_data['title'] = self.cleaned_data['title'].replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", '"').replace(u"\u201d", '"')
        
        if self.cleaned_data["article_type"] == 1:
            if self.cleaned_data['body'] == "":
                raise forms.ValidationError("Internal articles must have a body.")
        elif self.cleaned_data["article_type"] == 2:
            if not self.cleaned_data["external_url"]:
                raise forms.ValidationError("External articles must have a destination URL defined.")
        elif self.cleaned_data["article_type"] == 3:
            if not self.cleaned_data['external_url']:
                raise forms.ValidationError("Aggregated articles must have a destination URL defined.")

        return self.cleaned_data
    
class ArticleAdmin(VersionAdmin):

    
    form = ArticleAdminForm

    # This line is necessary because of Reversion, which defines its own change_list override. Without it, Reversion's version will take precedence.
    #change_list_template = "admin/content/change_list.html"
    
    list_display = ('title', 'status', 'publish_at', 'updated_at', 'show_authors_in_admin')
    prepopulated_fields = {"slug": ("title",),}
    list_filter = ('status', 'article_type', 'sites', 'publish_at',)
    ordering = ['-publish_at',]
    filter_horizontal = ['categories']
    date_hierarchy = 'publish_at'
    search_fields = ['title', 'abstract']
    actions = [delete_selected, make_public, make_draft]
    raw_id_fields = ('authors',)
    list_per_page = 50
    
    fieldsets = (
        ('Publish Form', {
            'fields': ('title', 'slug', 'dateline', ('publish_at', 'updated_at', 'expires_at'), 'authors', ('one_off_byline', 'one_off_credit_line'), 'abstract', 'body')
        }),
        ('Options', {
            'fields': (('status', 'featured'), ('article_type', 'external_url'), ('allow_comments', 'display_comments'))
        }),
        ('Categorization', {
            'fields': (('sites', 'primary_site'), 'categories')
        }),
    )
    

    def change_view(self, request, object_id):
        # check that we've got a valid object_id and raise a 404 if not
        try:
            int(object_id)
        except ValueError, e:
            raise Http404(str(e))
        return super(ArticleAdmin, self).change_view(request, object_id)

        

    
admin.site.register(Article, ArticleAdmin)
