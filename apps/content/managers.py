from datetime import datetime

from django.db import models
from django.conf import settings

class GenericContentManager(models.Manager):
    """
        Manager class which only displays results which have been published and are public.
    """
    def get_query_set(self):
        return super(GenericContentManager, self).get_query_set().filter(publish_at__lte = datetime.now(), status = 2, sites__id__exact=settings.SITE_ID).filter(models.Q(expires_at__isnull =True) | models.Q(expires_at__gte = datetime.now()))

    def all(self):
        return super(GenericContentManager, self).get_query_set().filter(publish_at__lte = datetime.now(), status = 2, sites__id__exact=settings.SITE_ID).filter(models.Q(expires_at__isnull =True) | models.Q(expires_at__gte = datetime.now()))

    def filter_is_future(self):
        return super(GenericContentManager, self).get_query_set().filter(publish_at__gte = datetime.now(), status = 2, sites__id__exact=settings.SITE_ID)

    def filter_is_draft(self):
        return super(GenericContentManager, self).get_query_set().filter(publish_at__lte = datetime.now(), status = 1, sites__id__exact=settings.SITE_ID)

    def filter_disallow_comments(self):
        return super(GenericContentManager, self).get_query_set().filter(publish_at__lte = datetime.now(), status = 2, allow_comments__exact=False, sites__id__exact=settings.SITE_ID)
