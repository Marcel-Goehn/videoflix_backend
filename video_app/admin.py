from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    readonly_fields = ('thumbnail_url',)

    def get_exclude(self, request, obj=None):
        if obj is None:
            return ('thumbnail_url',)
        return ()
