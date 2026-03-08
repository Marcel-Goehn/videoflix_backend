from django.urls import path
from .views import ListVideoView, HLSManifestView, HLSSegmentView

urlpatterns = [
    path("video/", ListVideoView.as_view(), name="video-list"),
    path("video/<int:movie_id>/<str:resolution>/index.m3u8",
         HLSManifestView.as_view(), name="hls-manifest"),
    path("video/<int:movie_id>/<str:resolution>/<str:segment>/",
         HLSSegmentView.as_view(), name="hls-segment"),
]
