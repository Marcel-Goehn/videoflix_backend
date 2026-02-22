from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    name = 'auth_app'

    def ready(self):
        """
        Needed to make usage of the signals
        """
        from .api import signals
