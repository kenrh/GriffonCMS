from apps.content.models import GenericContent

def make_public(modeladmin, request, queryset):
    """
        Sets content to public. Note we iterate and save, rather than doing an update(), because we need the post_save signals
        to fire.
    """
    try:
        for obj in queryset:
            obj.status = GenericContent.STATUS.public
            obj.save()
    except Exception:
        return HttpResponseServerError
make_public.short_description = 'Mark selected content as public'

def make_draft(modeladmin, request, queryset):
    """
        Sets content to draft. Note we iterate and save, rather than doing an update(), because we need the post_save signals
        to fire.
    """
    try:
        for obj in queryset:
            obj.status = GenericContent.STATUS.draft
            obj.save()
    except Exception:
        return HttpResponseServerError
make_draft.short_description = 'Mark selected content as draft'

def delete_selected(modeladmin, request, queryset):
    try:
        for obj in queryset:
            obj.delete()
    except Exception:
        return HttpResponseServerError
delete_selected.short_description = 'Delete selected'