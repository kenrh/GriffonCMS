import datetime

from django.conf import settings
from django.core.cache import cache
from django.template.defaultfilters import slugify
from django.contrib.sites.models import Site


def get_model_cache_key(content_class, id = None, site_id = None):
    """
        Returns the cache key string for the object corresponding to a content type model and a primary key.
        @type content_class: class
        @param content_class: A content object class.
        
        @type id: int
        @param id: The primary key corresponding to the object.
        
        @rtype: string
        @return: The cache key for the object.
    """
    module = slugify(str(content_class))
    if id:
        key = "%s::%s::%s::%s" % (settings.GROUP_NAME, module, id, settings.GROUP_CACHE_VERSION)
    else:
        key = key = "%s::%s::%s" % (settings.GROUP_NAME, module, settings.GROUP_CACHE_VERSION)
    if site_id:
        key = key + "::" + str(site_id)
    return key
    
def get_model_slug_cache_key(content_class, slug, site_id = None):
    """
        Returns the ID-based cache key string for the object corresponding to a content type model and a slug.
        @type content_class: class
        @param content_class: A content object class.
        
        @type slug: string
        @param slug: The slug corresponding to the object.
        
        @rtype: string
        @return: The cache key for the object.
    """
    module = slugify(str(content_class))
    key =  "%s::%s::%s::%s" % (settings.GROUP_NAME, module, slug, settings.GROUP_CACHE_VERSION)
    if site_id:
        key = key + "::" + str(site_id)
    return key

def resave_model_cache(sender, instance, created, **kwargs):
    """
        Recreates model cache keys after a save is performed, but doesn't cache if the user is staff or the object isn't public.
        If the user is staff, it deletes the cache keys.
        
        @type sender: class
        @param sender: The class originating the signal.
        
        @type instance: Model
        @param instance: The specific model originating the signal.
        
        @type created: boolean
        @param created: True if the save is sending a new object.
        
        @rtype: None
        @return: None
    """

    # To start with, kill the cache.
    try:
        if instance.id:
            cache.delete(get_model_cache_key(instance.__class__, instance.id))
            if hasattr(instance, "clear_cache"):
                instance.clear_cache()
            for site in Site.objects.all():
                cache.delete(get_model_cache_key(instance.__class__, instance.id, site.id))
                # Kill associated cache keys if applicable.
                if hasattr(instance, "clear_cache"):
                    instance.clear_cache(site.id)
                    
                
    except Exception, e:
        pass
        
    try:
        if instance.slug:
            cache.delete(get_model_slug_cache_key(instance.__class__, instance.slug))
            for site in Site.objects.all():
                cache.delete(get_model_slug_cache_key(instance.__class__, instance.slug, site.id))
    except Exception:
        pass
    

def delete_model_cache(sender, instance, **kwargs):
    """
        Deletes model cache keys after a deletion is performed.
        
        @type sender: class
        @param sender: The class originating the signal.
        
        @type instance: Model
        @param instance: The specific model originating the signal.
        
        @rtype: None
        @return: None

    """
    try:
        cache.delete(get_model_cache_key(instance.__class__, instance.id))
        if hasattr(instance, "clear_cache"):
            instance.clear_cache()
        for site in Site.objects.all():
            cache.delete(get_model_cache_key(instance.__class__, instance.id, site.id))
            # Kill associated cache keys if applicable.
            if hasattr(instance, "clear_cache"):
                instance.clear_cache(site.id)
    except Exception:
        pass
        
    try:
        cache.delete(get_model_slug_cache_key(instance.__class__, instance.slug))
        for site in Site.objects.all():
            cache.delete(get_model_slug_cache_key(instance.__class__, instance.slug, site.id))
    except Exception:
        pass


