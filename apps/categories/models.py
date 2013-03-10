from django.db import models
from django.template.defaultfilters import slugify

from treebeard.mp_tree import MP_Node

class Category(MP_Node):
    """
        @summary: need to add docs
        @todo: rework fields, write tests, write docs
        
        @var name: Category Name
        @type name: CharField
        
        @var slug: Hidden Autopopulated slug field
        @type slug: CharField
        
        @var path: Hidden Autopopulated path field
        @type path: TextField
        
    """
    name = models.CharField(max_length = 50)
    slug = models.CharField(max_length = 500, unique = True)


    def short_name(self):
        """return the short name"""
        return self.name
    short_name.admin_order_field = 'name'

    def __unicode__(self):
        """return the unicode repr"""
        return self.name

    def save(self, *args, **kwargs):
        """
            Additional save processing
        """ 

        # set the slug to be the path
        self.slug = slugify(self.path)

        # save the object
        super(Category, self).save(*args, **kwargs)

    
    class Meta:
        """model meta"""
        ordering = ['path']
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        

Category._meta.get_field('path').max_length = 1024