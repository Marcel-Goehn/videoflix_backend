from django.apps import AppConfig


class VideoConfig(AppConfig):
    name = 'video_app'

    def ready(self):
        """
        Needed to make usage of the signals
        """
        from .api import signals
