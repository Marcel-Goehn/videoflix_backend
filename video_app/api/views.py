import os

from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .serializers import ListVideoSerializer
from video_app.models import Video


@extend_schema(
    responses={200: ListVideoSerializer(many=True)},
    summary='List all videos',
    tags=['Video'],
)
class ListVideoView(ListAPIView):
    """
    Returns a list of all available videos.
    User needs to be authenticated to retrieve all videos.
    """
    queryset = Video.objects.all()
    serializer_class = ListVideoSerializer


@extend_schema(
    parameters=[
        OpenApiParameter('movie_id', int, OpenApiParameter.PATH, description='Video primary key'),
        OpenApiParameter('resolution', str, OpenApiParameter.PATH, description='Resolution label (e.g. 360p, 720p, 1080p)'),
    ],
    responses={
        200: OpenApiResponse(description='HLS m3u8 playlist'),
        404: OpenApiResponse(description='Video or manifest not found'),
    },
    summary='Get HLS manifest playlist',
    description='Returns the HLS master playlist for a specific video with the desired resolution. User needs to be authenticated.',
    tags=['Video'],
)
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


@extend_schema(
    parameters=[
        OpenApiParameter('movie_id', int, OpenApiParameter.PATH, description='Video primary key'),
        OpenApiParameter('resolution', str, OpenApiParameter.PATH, description='Resolution label (e.g. 360p, 720p, 1080p)'),
        OpenApiParameter('segment', str, OpenApiParameter.PATH, description='Segment filename (e.g. segment0.ts)'),
    ],
    responses={
        200: OpenApiResponse(description='HLS video segment (.ts)'),
        404: OpenApiResponse(description='Video or segment not found'),
    },
    summary='Get HLS video segment',
    description='Returns a single HLS video segment for a specific movie in the chosen resolution. User needs to be authenticated.',
    tags=['Video'],
)
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
