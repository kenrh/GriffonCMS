from datetime import datetime
import tempfile

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.http import Http404

from apps.utilities.managers.content_cache_manager import GenericContentCacheManager
from apps.utilities.cache.cache_utils import resave_model_cache, delete_model_cache
from apps.utilities.easychoice import EasyChoices, EasyChoice



######################################
# MLTAG
#######################################
class MLTag(models.Model):
    """
        Tag used to help organized media files.
        
        @type tag_name: CharField
        @cvar tag_name: The name of the tag

    """
    
    tag_name = models.CharField('tag', max_length=50, help_text="A tag to which media can be assigned to help sort them.")
    
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ('tag_name',)
        
    def __unicode__(self):
        return self.tag_name
        
        
        
######################################
# GFImage
#######################################       
CROP_DIRECTION_CHOICES = EasyChoices(
    EasyChoice(top=0, label='top'),
    EasyChoice(bottom=1, label='bottom'),
    EasyChoice(right=2, label='right'),
    EasyChoice(left=3, label='left'),
    EasyChoice(center=4, label='center'),
)

def default_image_path(instance, filename):
    """
        Generates the upload path used by the GFImage class' image field.
        Lowercases the extension and the filename, and removes spaces from the filename.
        
        @type instance: L{GFImage}
        @cvar instance: The GFImage whose image path is being determined.
        
        @type filename: string
        @cvar filename: The filename of the ImageField being passed in.
        
        @rtype: string
        @return: Returns a full path and name for the image.
    """
    # Sanitize the filename a bit.
    filename = filename.strip().lower()
    
    filename = "%s" % (filename)
    if instance.created_at:
        return "%s/%s/%s/%s/%s" % (settings.MEDIA_ROOT, settings.SITE_PREFIX, 'images', instance.created_at.strftime('%Y/%m/%d'), filename)
    else:
        return "%s/%s/%s/%s/%s" % (settings.MEDIA_ROOT, settings.SITE_PREFIX, 'images', datetime.now().strftime('%Y/%m/%d'), filename)

        
class GFImage(models.Model):
    """
        Photo content.

        @type title: CharField
        @cvar title: The title of the content.

        @type slug: SlugField
        @cvar slug: The URL-safe slug based on the title.

        @type image: ImageField
        @cvar image: The image the GFImage will use.

        @type crop_direction: PositiveSmallIntegerField
        @cvar crop_direction: Number representing the crop direction,
        which determines how the photo is cropped.

        @type created_at: DateTimeField
        @cvar created_at: Date/time stamp for when the file was uploaded.

        @type tags: L{MLTag}
        @cvar tags: MLTags assigned to the object to help sort it.

        @type objects: Manager
        @cvar objects: Default manager.

        @type cache: L{GenericContentCacheManager}
        @cvar cache: Manager which handles checking cache during views.

    """
    title = models.CharField('title', max_length = 200)
    slug = models.SlugField('slug', help_text = "This field will be filled in automatically when you save.")
    image = models.ImageField(upload_to=default_image_path, max_length=500)
    crop_direction = models.PositiveSmallIntegerField(choices=CROP_DIRECTION_CHOICES.choices(), default=4, help_text="""
        <p>The portion of the photo that will be shown when the photo is cropped.  The default is to crop to center.</p>
        <p>For example: If you're uploading a portrait shot you would want to select <strong>'top'</strong> to keep the subject's head from being removed.</p>
    """)
    created_at = models.DateTimeField('created at', auto_now_add = True)
    tags = models.ManyToManyField("MLTag", blank=True, null=True)
    objects = models.Manager()
    cache = GenericContentCacheManager()
    
    def __unicode__(self):
        return self.title
  
    def save(self, *args, **kwargs):
        """
            Overrides the base save function. Takes the image that was uploaded, resizes and crops it, and resaves it.
            
        """
        from PIL import Image, ImageOps
        import os
       
        try:
            # Delete the cache key for the image size used by RSS feeds
            cache_key = "%s::%s::%s::%s::%s::%s" % (settings.SITE_PREFIX, self.slug, 100, 100, settings.CACHE_VERSION, "size")
            cache.delete(cache_key)
        except Exception:
            pass
        
        # Perform the full save and DB commit.
        super(GFImage, self).save(*args, **kwargs)
        
        # full_image_path is the image's path.
        full_image_path = self.image.name
            
        if os.path.isfile(full_image_path):
            # extract info from the image name
            image_base_path, image_name_with_ext = os.path.split(full_image_path) # ('/home/media/TEST/images', 'ellena.jpg')
            
            # make sure the destination directory exists
            try:
                os.makedirs(image_base_path)
            except OSError, e:
                pass

            # resize the image if it needs it and save it with the new name
            # Normally, you could just use im = Image.open(image_path) without worrying about closing.
            # However, due to occasional file locking errors, I am explictly telling PIL how to handle the opening, loading, and closing.
            fp = open(full_image_path, "rb")
            im = Image.open(fp)
            im.load()
            fp.close()
            
            new_width = 1280
            
            # Only resave if you need to resize the image
            if im.size[0] > new_width:
                aspect_ratio = float(im.size[0]) / float(im.size[1])
                new_height = int(new_width / float(aspect_ratio))
                # Save transparency info, as the resize function drops it
                try:
                    transparency = im.info['transparency']
                except Exception:
                    transparency = 0
                # Save the file. Save throws an exception if it fails somehow, and may have created a partial file which would need to be deleted.
                try:
                    new_im = ImageOps.fit(im, (new_width, new_height), Image.ANTIALIAS)
                    # Reassign transparency info
                    new_im.info['transparency'] = transparency
                    new_im.save(full_image_path)
                except Exception:
                    os.remove(full_image_path)
            

    def delete(self):
        """
            If a GFImage object is deleted, this function removes the file it was attached to as well.
        """
        import os
        try:
            os.remove(self.image.name)
        except Exception:
            pass
        
        try:
            # If that was the last image in that day, delete the dir.
            folder_path = self.image.name.rsplit('/', 1)[0]
            if len(os.listdir(folder_path)) < 1:
                os.rmdir(folder_path)
                
            # If that was the last image in that month, delete the dir.
            folder_path = folder_path.rsplit('/', 1)[0]
            if len(os.listdir(folder_path)) < 1:
                os.rmdir(folder_path)
                
            # If that was the last image in that year, delete the dir.
            folder_path = folder_path.rsplit('/', 1)[0]
            if len(os.listdir(folder_path)) < 1:
                os.rmdir(folder_path)
        except Exception:
            pass
            
        super(GFImage, self).delete()
        
    def determine_mime_type(self):
        """
            Determines the image's mime-type based on its extension.
            Defaults to image/png.
            
            @rtype: string
            @return: The mime type of the image.
        """
        extension = self.image.name.rsplit(".")
        # Get the last chunk of the list
        extension = extension[len(extension) -1]
        extension = extension.lower()
        
        if extension == "jpg" or extension == "jpeg":
            type = "image/jpeg"
        elif extension == "gif":
            type = "image/gif"
        elif extension == "png":
            type = "image/png"
        else:
            type = "image/jpeg"
        return type
        
    
    def determine_format(self):
        """
            Determines the image's format based on its extension.
            Defaults to image/png.
            
            @rtype: string
            @return: The format of the image.
        """
        extension = self.image.name.rsplit(".")
        # Get the last chunk of the list
        extension = extension[len(extension) -1]
        extension = extension.lower()
        
        if extension == "jpg" or extension == "jpeg":
            type = "JPEG"
        elif extension == "gif":
            type = "GIF"
        elif extension == "png":
            type = "PNG"
        else:
            type = "JPEG"
        return type
        
    def get_absolute_url(self):
        """Provide the full photo URL."""
        return 'http://%s/gfmedia/image/full/%s/%s/' % (settings.SITE_DOMAIN, self.id, self.slug)
    
    def get_resize_url(self, width, height):
        """
            Provide the resized version of the photo URL.
            
            @param width: Width of the desired resized image.
            @type width: int
        
            @param height: Height of the desired resized image.
            @type height: int
            
            @rtype: string
            @return: The URL of the resized image.
        """
        return 'http://%s/gfmedia/image/%s/%s/%s/%s/' % (settings.SITE_DOMAIN, width, height, self.id, self.slug)
    
    
    def get_resized_size(self, width, height):
        """
            Returns the size of a resized image, in bytes.
            Note that this is pretty much identical to the view that resizes an image, except that it returns the size instead of the image.
        """
        from PIL import Image, ImageOps
        
        cache_key = "%s::%s::%s::%s::%s::%s" % (settings.SITE_PREFIX, self.slug, width, height, settings.CACHE_VERSION, "size")
        size = cache.get(cache_key)
    
        if not size:
            # Return None if the file cannot be found.
            try:
                im = Image.open(self.image.name)
            except Exception:
                return None
            
            # Mode conversion depends on the file format. PNGs use Palette mode in order to preserve transparency.
            use_transparency = True
            try:
                if self.determine_format() == 'PNG':
                    try:
                        im = im.convert("P", palette=Image.ADAPTIVE)
                    except ValueError:
                        im = im.convert("RGB", palette=Image.ADAPTIVE)
                        use_transparency = False
                else:
                    im = im.convert("RGB", palette=Image.ADAPTIVE)
            except IOError, e:
                raise Http404(str(e))
                
            photo_width, photo_height = im.size
            
            # resize the photo
            if int(width) <= 4000 and int(height) <= 10000:
                new_width = int(width)
                new_height = int(height)
                
                # if width or height is zero then resize the image based on the non-zero dimension while
                # keeping the image's aspect ratio
                if int(width) == 0:
                    aspect_ratio = float(photo_width) / float(photo_height)
                    new_width = new_height * float(aspect_ratio)
                elif int(height) == 0:
                    aspect_ratio = float(photo_height) / float(photo_width)
                    new_height = new_width * float(aspect_ratio)
                
                if self.crop_direction == 0:
                    crop_direction = (0.5, 0.0)
                elif self.crop_direction == 1:
                    crop_direction = (0.5, 1.0)
                elif self.crop_direction == 2:
                    crop_direction = (1.0, 0.5)
                elif self.crop_direction == 3:
                    crop_direction = (0.0, 0.5)
                elif self.crop_direction == 4:
                    crop_direction = (0.5, 0.5)
                
                new_width = int(new_width)
                new_height = int(new_height)
                
                # Save transparency info, as the resize function drops it
                try:
                    transparency = im.info['transparency']
                except Exception:
                    transparency = 0
                # run the resize
                im = ImageOps.fit(im, (new_width, new_height), Image.ANTIALIAS, 0, crop_direction)
                im.info['transparency'] = transparency
            else:
                return None
            
            # open a temp file and save the newly resized image
            # This can go wrong; if it does, throw a server error so it can be examined.
            try:
                tmp_file = tempfile.NamedTemporaryFile('w+b')
                if use_transparency == True:
                    im.save(tmp_file, self.determine_format(), quality=90, transparency=transparency)
                else:
                    im.save(tmp_file, self.determine_format(), quality=90)
                f = open(tmp_file.name)
                resized_photo = f.read()
                f.close()
                tmp_file.close()
                
                size = len(resized_photo)
                cache.set(cache_key, size, settings.CACHE_LONG_SECONDS)   
            except Exception:
                return None
        return size

    def get_height(self):
        """ Returns the height of the image. Wraps the ImageField attribute for doing so, in case it needs to be cached later. """
        try:
            return self.image.height
        except Exception:
            return 0
        
    def get_width(self):
        """ Returns the width of the image. Wraps the ImageField attribute for doing so, in case it needs to be cached later. """
        try:
            return self.image.width
        except Exception:
            return 0
        
    def fits_section_header(self):
        """ Returns True if the image is the correct portions for a graphical section header, 660 x 65. """
        if self.get_width() == 660 and self.get_height() == 65:
            return True
        else:
            return False
        
    def show_image(self):
        """Show a thumbnail image in the admin."""
        return "<a href='%s'><img src='%s' /></a>" % (self.get_absolute_url(), self.get_resize_url(100, 100))
    show_image.allow_tags = True
    show_image.short_description='Image'
    
    def show_tags(self):
        """ Shows the MLTags assigned to the image. """
        tags = ''
        for tag in self.tags.all():
            tags += tag.tag_name
            tags += " "
        return tags
    show_tags.short_description='Tags'
    
    
    
    
    class Meta:
        get_latest_by = "publish_at"
        verbose_name = "Image"
        verbose_name_plural = "Image Library"
        
post_save.connect(resave_model_cache, sender=GFImage)   
post_delete.connect(delete_model_cache, sender=GFImage)        
        
     
######################################
# FREQUENTIMAGE
#######################################

class FrequentImage(models.Model):
    """
        Provides a library of frequently used images that can be attached to articles, i.e an image that says 'Breaking News'.
        
        @type title: CharField
        @cvar title: The title of the content.
        
        @type photo: L{GFImage}
        @cvar photo: The GFImage the image represents.
        
        @type sites: L{Site}
        @cvar sites: The sites the image is assigned to.

    """
    
    title = models.CharField('title', max_length = 200)
    image = models.ForeignKey(GFImage)
    sites = models.ManyToManyField(Site)
    objects = models.Manager()
    cache = GenericContentCacheManager()
    
    def __unicode__(self):
        return self.title
        
    def get_absolute_url(self):
        return self.image.get_absolute_url()
    
    def show_image(self):
        """Show a thumbnail image in the admin."""
        return "<a href='%s'><img src='%s' /></a>" % (self.image.get_absolute_url(), self.image.get_resize_url(100, 100))
    show_image.allow_tags = True
    show_image.short_description='Image'
    
    class Meta:
        verbose_name = "Frequently Used Image"
        verbose_name_plural = "Frequently Used Images"
        permissions = (
            ('view_frequentimage', 'Can view Frequently Used Image'),
        )
