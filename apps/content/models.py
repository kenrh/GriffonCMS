from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from apps.categories.models import Category
from apps.content.managers import GenericContentManager
from apps.utilities.easychoice import EasyChoice, EasyChoices

######################################
# GENERIC CONTENT
#######################################
class GenericContent(models.Model):
    """
        @summary: Generic Content Object Model. To be used as base fields for all content objects
        
        @type title: CharField
        @cvar title: The title of the content.
        
        @type slug: SlugField
        @cvar slug: The URL-safe slug based on the title.
        
        @type status: IntegerField
        @cvar status: Determines if article is public or not.
        
        @type allow_comments: BooleanField
        @cvar allow_comments: Whether to allow comments.
        
        @type display_comments: BooleanField
        @cvar display_comments: Whether to display existing comments.
        
        @type created_at: DateTimeField
        @cvar created_at: Date content was created.
        
        @type publish_at: DateTimeField
        @cvar publish_at: Date content is to appear on the site.
        
        @type updated_at: DateTimeField
        @cvar updated_at: Date of last update. Set to the current time by default.
        
        @type one_off_byline: CharField
        @cvar one_off_byline: The author of the content, used if no staff member(s) are mapped to it.
        
        @type one_off_credit_line: CharField
        @cvar one_off_credit_line: The source of the content, used if no staff member(s) are mapped to it.
        
        @type abstract: TextField
        @cvar abstract: The description of the content.
        
        @type authors: L{Profile}
        @cvar authors: Profiles of authors assigned to the content.

        @type published: L{GenericContentManager}
        @cvar published: The QuerySet for the object, screened to include only objects which are set to public and are published.
        
        @type objects: L{Manager}
        @cvar objects: Base QuerySet for the object.
        
        @type sites: L{Site}
        @cvar sites: The sites to which the content belongs.
        
        @type categories: L{Category}
        @cvar categories: The categories to which the content belongs.
        
    """
    STATUS_CHOICES = EasyChoices(
        EasyChoice(draft=1, label='Draft'),
        EasyChoice(public=2, label='Public'),
    )

    title = models.CharField('title', max_length = 200)
    slug = models.SlugField('slug', help_text = "This field will be filled in automatically when you save.")
    status = models.IntegerField('status', choices = STATUS_CHOICES, default = 2, help_text = "Content marked as Draft will be visible to staff only.")
    allow_comments = models.BooleanField('allow comments', default = True, help_text = "If unchecked, users will not be allowed to leave new comments, but existing ones will be displayed.")
    display_comments = models.BooleanField('display comments', default = True, help_text = "If unchecked, existing comments will not be shown and new comments will not be allowed.")
    featured = models.BooleanField('featured', default=False, help_text="When a List is displayed, it may be set to move the most recently updated content flagged as featured to the top.")
    created_at = models.DateTimeField(auto_now_add = True)
    publish_at = models.DateTimeField('published date', default = datetime.now)
    updated_at = models.DateTimeField('updated date', blank = True, help_text="If left blank, this will be set to the publish time.", db_index=True)
    expires_at = models.DateTimeField('expiration date', blank=True, null=True, help_text="The time at which this content will no longer be publicly visible.")
    one_off_credit_line = models.CharField('credit line', max_length = 200, help_text="The source of the content.", blank = True)
    one_off_byline = models.CharField('byline', max_length = 200, help_text="Replaces the staff member selection as the content author.", blank = True)
    abstract = models.TextField(help_text = "The summary/explanation of what the content depicts.")
    authors = models.ManyToManyField(User)
    sites = models.ManyToManyField(Site, help_text='The sites that this content will display on.')
    primary_site = models.ForeignKey(Site, related_name="%(class)s_primary_site", blank=True, null=True, help_text='If the content is set to display on multiple sites, setting this value will mandate that the content only opens in the wrapper of the selected site, no matter which site the content appears on.')
    categories = models.ManyToManyField(Category, help_text='The categories that the content will be a part of. You can select multiple categories, and categories are hierarchical (i.e., choosing news.local will mean the content is also a part of news).')
    objects = models.Manager()
    published = GenericContentManager()
    cache = GenericContentCacheManager()


    class Meta:
        abstract = True
        ordering = ('-updated_at',)
        get_latest_by = 'updated_at'
        

    def get_version_number(self):
        """
            Return the Reversion number of the content.
        """
        ctype = self.get_content_type_id()
        cache_key = get_model_cache_key(self.__class__, self.id) + "::versions"
        number = cache.get(cache_key)
        if not number:
            number = Version.objects.filter(content_type__id = ctype, object_id = unicode(self.id)).only('id').count()
            cache.set(cache_key, number, settings.CACHE_LONG_SECONDS)
        return number

    def open_in_new_window(self):
        """
            Whether a content object should open in a new window when its link is hit.
            This generic version always returns False, and individual content object classes can override it with their own behavior.
        """
        return False
    
    
    def is_content_object(self):
        """ Simple function to affirm object is a content object. """
        return True
        
           
    def get_comment_count(self, from_admin = False):
        """
            Return the number of comments attached to the comments.
            
            @param from_admin: Boolean value. If true, the request is assumed to be from the admin and bypasses memcache.
            @type from_admin: boolean
            
            @rtype: int
            @return: Number of ThreadedComments assigned to the object.
        """
        ctype = self.get_content_type_id()
        cache_key = get_model_cache_key(self.__class__, self.id) + "::commentcount"
        if from_admin == False:
            num_comments = cache.get(cache_key)
        else:
            num_comments = None
            
        if num_comments == None:
            num_comments = ThreadedComment.public.filter(content_type__id = ctype, object_id__exact = self.id, is_approved = True, user__is_active=True).only('id').count()
            if from_admin == False:
                cache.set(cache_key, num_comments, settings.CACHE_LONG_SECONDS)
        
        return num_comments 

    def get_vote_count(self, from_admin = False):
        """
            Returns the vote score of the content.
            
            @param from_admin: Boolean value. If true, the request is assumed to be from the admin and bypasses memcache.
            @type from_admin: boolean
            
            @rtype: list
            @return: List of Vote objects assigned to the object.
        """
        vote_score = Vote.objects.get_score(self)
        
        return vote_score

    def get_rating_count(self, from_admin = False):
        """
            Returns the rating of the content.
            
            @param from_admin: Boolean value. If true, the request is assumed to be from the admin and bypasses memcache.
            @type from_admin: boolean
            
            @rtype: list
            @return: List of Rating objects assigned to the object.
        """
        rate_score = Ratings.objects.get_score(self)

        return rate_score
        
    def show_comment_count_with_admin_url(self):
        """
            Displays the number of comments attached to content in the admin.
        """
        ctype = ContentType.objects.get_for_model(self)
        return '<a target="_blank" href="/admin/threadedcomments/threadedcomment/?content_type__pk=%d&object_id__exact=%d">( %d ) View</a>' % (ctype.id, self.id, self.get_comment_count(from_admin=True))
    show_comment_count_with_admin_url.allow_tags = True
    show_comment_count_with_admin_url.short_description='Comments'

    def show_rating_count_with_admin_url(self):
        ctype = ContentType.objects.get_for_model(self)
        rating_count = self.get_rating_count(from_admin=True)
        return '<a target="_blank" href="/admin/rating/ratings/?content_type__pk=%d&object_id__exact=%d">( Score of %s out of %s votes ) View</a>' % (ctype.id, self.id, rating_count['score'], rating_count['num_votes'])
    show_rating_count_with_admin_url.allow_tags = True
    show_rating_count_with_admin_url.short_description='Ratings'

    def show_vote_count_with_admin_url(self):
        ctype = ContentType.objects.get_for_model(self)
        vote_count = self.get_vote_count(from_admin=True)
        return '<a target="_blank" href="/admin/django_voting/vote/?content_type__pk=%d&object_id__exact=%d">( Score of %s out of %s votes ) View</a>' % (ctype.id, self.id, vote_count['score'], vote_count['num_votes'])
    show_vote_count_with_admin_url.allow_tags = True
    show_vote_count_with_admin_url.short_description='Votes'
    
    
    def show_authors_in_admin(self):
        """
            Displays the author(s) for content, or, if it's filled out, the byline.
        """
        authors = ''
        if self.one_off_byline:
            authors = self.one_off_byline
        else:
            for author in self.authors.all():
                authors += str(author) + ', '
            # Truncate the trailing comma, but catch the error just in case there somehow were no authors.
            try:
                authors = authors.rsplit(", ", 1)[0]
            except KeyError:
                pass
        
        return authors
        
    show_authors_in_admin.allow_tags = True
    show_authors_in_admin.short_description='Author(s)/Byline'

    def is_public(self):
        """
            Determines if a content object is public by checking its status and publish date.
            
            @rtype: boolean
            @return: True if article is public, False otherwise.
        """
        if self.status == GenericContent.STATUS_CHOICES.public and self.publish_at <= datetime.now() and (not self.expires_at or self.expires_at >= datetime.now()):
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        """
            If no updated date is defined, it becomes the publish date.
            No updated date can pre-date the publish date.
        """
        if not self.updated_at or self.updated_at < self.publish_at:
            self.updated_at = self.publish_at
        
        if self.expires_at:
            if self.expires_at < self.publish_at:
                self.expires_at = self.publish_at
           
        super(GenericContent, self).save(*args, **kwargs)
            
    def __unicode__(self):
        """
            returns unicode __str__ for model
        """
        return self.title

    def get_categories(self):
        """
            Since categories are hierarchical, using self.categories.all() doesn't return the whole picture. This will return a list of all categories the content is in,
            plus their parents, ordered by path. Returns None if there are no categories.
            
            @rtype: list or None
            @return: A list of L{Category} objects sorted by path, or None if no categories were found.
        """
        categories = self.categories.all()

        cache_key = get_model_cache_key(self.__class__, self.id) + "::categories"
        final_cats = cache.get(cache_key)
        if not final_cats:
            final_cats = []
            # Iterate through the member categories
            for category in categories:
                # If it isn't in the final list, add it
                if category not in final_cats:
                    final_cats.append(category)
                # Get all the categories ancestors, and if they aren't in the list, add them.
                for cat in category.get_ancestors():
                    if cat not in final_cats:
                        final_cats.append(cat)
            
            # Sort the whole thing by path, or set the list to None if nothing was found.
            if len(final_cats) > 0:        
                final_cats.sort(lambda x,y: cmp(x.path, y.path))
            else:
                final_cats = None
            
            cache.set(cache_key, final_cats, settings.CACHE_LONG_SECONDS)
        
        return final_cats
        

    def get_photo(self):
        """
            Function which returns the top MGImage associated with the content. Defined here to make it safe to query any content object in this way.
        """
        return None
        
    def get_video(self):
        """
            Function which returns the top Video associated with the content. Defined here to make it safe to query any content object in this way.
        """
        return None




######################################
# ARTICLE
#######################################
class Article(GenericContent):
    """
        Article content.
        
        @type body: TextField
        @cvar body: The body of the article.
        
        @type abstract: TextField
        @cvar abstract: The abstract of the article.
        
        @type newsletter_tease: TextField
        @cvar newsletter_tease: The abstract of the article, used for email, overrides the abstract in such cases.
        
        @type mobile_tease: TextField
        @cvar mobile_tease: The abstract of the article, used for mobile, overrides the abstract in such cases.
        
        @type dateline: CharField
        @cvar dateline: The location of the article.
        
        @type subhead: CharField
        @cvar subhead: The kicker of the article.
        
        @type article_type: IntegerField
        @cvar article_type: Type of article. 1=Internal, 2=External, 3=Aggregated.
        
        @type open_behavior: IntegerField
        @cvar open_behavior: How an Aggregated article should be opened.
        
        @type external_url: URLField
        @cvar external_url: If an article is external, it will lead to this URL.
        
        @type parse_file: URLField
        @cvar parse_file: Internal use; undetermined.
        
        @type stock_image: L{FrequentImage}
        @cvar stock_image: A stock image used in place of associated Photos.
        
        @type poll: L{Poll}
        @cvar poll: An associated poll.        
        
    """
    TYPE_CHOICES = EasyChoices(
        EasyChoice(internal=1, label='Internal'),
        EasyChoice(aggregated=2, label='Aggregated'),
    ) 
    
    
    body = models.TextField('body', help_text = 'The main body of the article.', blank = True)
    footer = models.TextField('footer', help_text = 'Miscellaneous information to be appended to the body, such as contributing reporters.', blank=True)
    dateline = models.CharField('dateline', max_length = 200, help_text = "The location of the article. i.e, SPARTANBURG, S.C.", blank = True)
    article_type = models.IntegerField('article type', choices = TYPE_CHOICES.choices(), default = TYPE_CHOICES.internal, help_text = 'Internal - Normal article. External - Links to another site. Aggregated - Brought in by RSS from another site/URL.')
    external_url = models.CharField('external url', max_length = 300, help_text = "If the article is external, its link will be rendered as this URL. The URL should include the 'http://'.", blank = True)
    poll = models.ForeignKey(Poll, blank=True, null=True, help_text='A poll associated with the article.')  

    
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        get_latest_by = "updated_at"