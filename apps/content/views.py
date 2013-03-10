from datetime import date
import time

from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect, HttpResponseServerError
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.conf import settings
from django.core.cache import cache
from django.db.models.loading import get_model
from django.template import loader, RequestContext
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_headers
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from apps.utilities.cache.cache_utils import get_model_cache_key, get_model_slug_cache_key
from apps.content.models import GenericContent, Article
from apps.contentinfo.models import GFContentType

######################################
# CONTENT DETAIL
#######################################
def content_display(request, slug, year, month, day, content_type, id):
    """
        Main view function.
        
        @param request: Django HttpRequest object.
        @type request: L{HttpRequest}

        @param slug: URL safe version of content's title.
        @type slug: string
        
        @param year: 4-digit year content was published.
        @type year: int
        
        @param month: 3-letter abbreviation of month content was published.
        @type month: string
        
        @param day: 2-digit day content was published.
        @type day: int
        
        @param id: Database PK of content.
        @type id: int
        
        @rtype: L{HttpResponse}
        @return: HttpResponse encompassing the content's detail page or its generic views.
    """

    # Validate the url contains a valid date
    try:
        valid_date = date(*time.strptime(year+month+day, '%Y%b%d')[:3])
    # if no valid date, return a 404 error
    except ValueError:
        raise Http404('Invalid date.')
    
    # Determine the content type. This will help us look up the cache key for the object.
    ctype_cache_key = "%s::contenttype::%s::%s" % (settings.GROUP_NAME, str(content_type).lower(), settings.GROUP_CACHE_VERSION)
    content_type_name = cache.get(ctype_cache_key)
    if not content_type_name:
        content_type_name = get_object_or_404(GFContentType, short_name__iexact=content_type).model_name
        cache.set(ctype_cache_key, content_type_name, settings.CACHE_LONG_SECONDS)
    try:
        content_type = get_model('content', content_type_name.lower())
    except Exception:
        return HttpResponseServerError
    
    # Object Cache Key
    cache_key = get_model_cache_key(content_type, id, settings.SITE_ID)

    # If the URL has ?clear_cache on it, and the user is staff, clear the cache despite any other timers/settings.
    # Otherwise, check the settings/timers normally.
    if request.GET.has_key('clear_cache') and request.user.is_staff:
        clear_cache = True
    else:
        clear_cache = False
 
    content_obj = None   
    if not clear_cache:   
        # does the settings.CACHE_HTML global variable not equal None. If so, check HTML cache and return.
        if settings.CACHE_HTML:
            # If settings for caching entrie HTML page is set then build the html page cache key
            html_cache_key = "%s.html" % cache_key
            # after building the html page cache key, check the cache to see if page exists
            html = cache.get(html_cache_key)
            # if page exists, return the cached page
            if html:
                return html
            # if page does not exits, fall through and build html that will be cached and rendered
        
        # Try cache retrieval for object
        content_obj = content_type.cache.get(id=id)
    
    # If cache get failed or cache was ordered to clear, find the content object from the DB.
    if not content_obj:
        # if the user is not staff, only select from published, public articles
        if not request.user.is_staff:
            # get the obj
            content_obj = get_object_or_404(content_type.published, id=id, sites__id__exact=settings.SITE_ID)

            # Don't cache staff requests, or else they'll be visible to all once cached.
            model_key = get_model_cache_key(content_type, content_obj.id, settings.SITE_ID)
            slug_key = get_model_slug_cache_key(content_type, content_obj.slug, settings.SITE_ID)
            cache.set(model_key, content_obj, settings.CACHE_LONG_SECONDS)
            cache.set(slug_key, model_key, settings.CACHE_LONG_SECONDS)
            
        # if the user is staff, they are allowed to see draft/non-published articles
        else:
            content_obj = get_object_or_404(content_type.objects, id=id, sites__id__exact=settings.SITE_ID)
            # Axe any cache for the object to be sure it is all clear.
            if clear_cache:
                model_key = get_model_cache_key(content_type, content_obj.id, settings.SITE_ID)
                slug_key = get_model_slug_cache_key(content_type, content_obj.slug, settings.SITE_ID)
                cache.delete(model_key)
                cache.delete(slug_key)
    
    # Get the absolute URL.
    try:
        absolute_url = content_obj.get_absolute_url()
    except Exception, e:
        raise Http404(str(e))
  
    # Some content types have external types that go offsite.
    if hasattr(content_obj, "article_type"):
        if content_obj.article_type == Article.TYPE_CHOICES.external or content_obj.article_type == Article.TYPE_CHOICES.aggregated:
            return HttpResponsePermanentRedirect(absolute_url)

    # One of the tricky things about caching via ID is that, once cached, it ceases to care what the slug is because it's pulling cache by the ID passed in. Validate the slug.
    if content_obj.slug != slug:
        return HttpResponsePermanentRedirect(absolute_url)
     
    # If the date passed in through the URL doesn't match the content's actual publish date, 301 redirect to the correct URL.
    if content_obj.publish_at.date() != valid_date:
        return HttpResponsePermanentRedirect(absolute_url)
    
    # assign the rendered template to a variable that can be cached and/or rendered
    template = "content/"
    template += str(content_type_name).lower()
    template += "_detail.html"
    context_dict = {
        'content': content_obj,
    }
    html = render_to_response(template, context_dict, context_instance=RequestContext(request))
    
    # If HTML caching is on, cache the result before returning
    if settings.CACHE_HTML and not request.user.is_staff:
        cache.set(html_cache_key, html, settings.CACHE_HTML)
    
    return html