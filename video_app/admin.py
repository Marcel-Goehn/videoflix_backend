from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    Makes sure that the thumbnail_url can't be modified manually in the admin interface
    or by sending a request
    """
    readonly_fields = ('thumbnail_url',)

    def get_exclude(self, request, obj=None):
        if obj is None:
            return ('thumbnail_url',)
        return ()
