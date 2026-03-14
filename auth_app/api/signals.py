from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

import django_rq

from .utils import account_activation_token, send_activation_email


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Sends an activation email after a user has successfully created an account.
    """
    if created:
        queue = django_rq.get_queue("default", autocommit=True)
        activation_url = (
            f"http://127.0.0.1:5500/pages/auth/activate.html"
            f"?uid={urlsafe_base64_encode(force_bytes(instance.pk))}"
            f"&token={account_activation_token.make_token(instance)}"
        )
        queue.enqueue(send_activation_email, instance.email, instance.username, activation_url)