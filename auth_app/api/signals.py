import os

from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail

import django_rq

from .utils import encode_id

from dotenv import load_dotenv

load_dotenv()


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Sends an activation email after a user has successfully created an account.
    """
    if created:
        print(instance)
        queue = django_rq.get_queue("default", autocommit=True)
        queue.enqueue(send_mail,
                      "Confirm your email",
                      f"""Dear {instance.email},
                      Thank you for registering with Videoflix. To complete your registration and verify your email address, please click the link below:

                      http://127.0.0.1:8000/api/activate/{encode_id(instance.pk)}/token/

                      If you did not create an account with us, please disregard this email.

                      Best regards,

                      Your Videoflix Team.""",
                      os.environ.get("EMAIL_HOST_USER"),
                      [instance.email],
                      fail_silently=False)