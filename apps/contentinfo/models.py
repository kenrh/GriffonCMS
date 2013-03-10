from django.db import models

######################################
# CONTENT TYPE
#######################################
class GFContentType(models.Model):
    """
        @summary: The list of content types usable for content objects. Think of it as a filter on the contrib content types, showing only content types we want users to see.

        @type full_name: CharField
        @cvar full_name: The human readable version of the content type's name.

        @type model_name: CharField
        @cvar model_name: The name of the content type's model.

        @type short_name: CharField
        @cvar short_name: The abbreviation of the content type used to identify it in URLs.

    """
    full_name = models.CharField('full name', max_length = 200, help_text="The public name of the content type, such as Article.")
    model_name = models.CharField('model name', max_length = 200, help_text="The name of the model which the content feeds off of in the content.models file.")
    short_name = models.CharField('short name', max_length = 2, help_text="The name by which the content is identified through URLs, such as ar for Article.")
    
    class Meta:
        verbose_name = "GF Content Type"
        verbose_name_plural = "GF Content Types"
        ordering = ["full_name"]
        
    def __unicode__(self):
        """
            returns unicode __str__ for model
        """
        return self.full_name
