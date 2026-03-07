from django.urls import path
from .views import ListVideoView

urlpatterns = [
    path("video/", ListVideoView.as_view(), name="video-list")
]