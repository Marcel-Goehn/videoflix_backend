from rest_framework import serializers

from video_app.models import Video


class ListVideoSerializer(serializers.ModelSerializer):
    """
    Serializes a list of all available videos.
    """
    class Meta:
        model = Video
        fields = ["id", "created_at", "title", "description",
                  "thumbnail_url", "category"]
        read_only_fields = ["id", "created_at", "title", "description",
                            "thumbnail_url", "category"]
