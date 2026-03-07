from rest_framework.generics import ListAPIView

from .serializers import ListVideoSerializer
from video_app.models import Video


class ListVideoView(ListAPIView):
    """
    Returns a list of all available videos.
    User needs to be authenticated to retrieve all videos.
    """
    queryset = Video.objects.all()
    serializer_class = ListVideoSerializer