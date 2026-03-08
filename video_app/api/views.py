import os

from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ListVideoSerializer
from video_app.models import Video


class ListVideoView(ListAPIView):
    """
    Returns a list of all available videos.
    User needs to be authenticated to retrieve all videos.
    """
    queryset = Video.objects.all()
    serializer_class = ListVideoSerializer


class HLSManifestView(APIView):
    """
    Returns the HLS master playlist for a 
    specific video with the desired resolution
    """
    def get(self, request, movie_id, resolution):
        if not Video.objects.filter(pk=movie_id).exists():
            return Response(
                {"Error": "Video not found"},
                status=status.HTTP_404_NOT_FOUND)
        manifest_path = os.path.join(
            settings.MEDIA_ROOT, 'hls', str(movie_id), resolution, 'index.m3u8'
        )
        if not os.path.exists(manifest_path):
            return Response(
                {"Error": "Video or manifest not found"},
                status=status.HTTP_404_NOT_FOUND)
        with open(manifest_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/vnd.apple.mpegurl')


class HLSSegmentView(APIView):
    """
    Returns a single HLS video segment for a specific movie in the chosen resolution.
    """
    def get(self, request, movie_id, resolution, segment):
        if not Video.objects.filter(pk=movie_id).exists():
            return Response(
                {"Error": "Video not found"},
                status=status.HTTP_404_NOT_FOUND)
        segment_path = os.path.join(
            settings.MEDIA_ROOT, 'hls', str(movie_id), resolution, segment
        )
        if not os.path.exists(segment_path):
            return Response(
                {"Error": "Video or segment not found"},
                status=status.HTTP_404_NOT_FOUND)
        with open(segment_path, 'rb') as f:
            content = f.read()
        return HttpResponse(content, content_type='video/MP2T')
