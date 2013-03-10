from django.db import models
from django.core.cache import cache
from django.conf import settings

from apps.utilities.cache.cache_utils import get_model_slug_cache_key, get_model_cache_key

class GenericContentCacheManager(models.Manager):
    """
        Manager class which returns the cached value based on cache_key, slug or id

        @param id: accepts object ID

        @param slug: accepts object slug

        @param cache_key: accepts object cache key

        @return: content object from cache or None.  Will need to test response and do db api call if necessary
    """
    def get(self, id = None, slug = None, cache_key = None):
        if cache_key:
            return cache.get(cache_key)
        elif slug:
            slug_cache_key = get_model_slug_cache_key(self.model, slug, settings.SITE_ID)
            id_cache_key = cache.get(slug_cache_key)
            return cache.get(id_cache_key)
            # lookup and return
        elif id:
            # lookup and return
            cache_key = get_model_cache_key(self.model, id, settings.SITE_ID)
            return cache.get(cache_key)
        else:
            return None

