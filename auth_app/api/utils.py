import os
import six

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from email.mime.image import MIMEImage

import django_rq

from dotenv import load_dotenv


load_dotenv()


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Creates a unique token to verify email requests.
    """

    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


account_activation_token = AccountActivationTokenGenerator()


def send_activation_email(to_email, username, activation_url):
    """
    Sends an email after registration to activate the user
    """
    subject = "Confirm your email"
    context = {
        "username": username,
        "activation_url": activation_url,
    }
    html_message = render_to_string("auth_app/activation_email.html", context)
    plain_message = strip_tags(html_message)
    from_email = os.getenv("EMAIL_HOST_USER")

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=from_email,
        to=[to_email],
    )
    email.attach_alternative(html_message, "text/html")

    img_path = os.path.join(settings.BASE_DIR, "auth_app",
                            "static", "auth_app", "images", "Logo.png")
    with open(img_path, "rb") as f:
        img = MIMEImage(f.read())
        img.add_header("Content-ID", "<logo>")
        img.add_header("Content-Disposition", "inline", filename="Logo.png")
        email.attach(img)

    email.send()


def do_send_password_reset(to_email, reset_url):
    """
    Sends an email to verify that the password reset request is really coming
    from the actual user
    """
    subject = "Reset your Password"
    context = {
        "reset_url": reset_url
    }
    html_message = render_to_string("auth_app/password_reset_email.html", context)
    plain_message = strip_tags(html_message)
    from_email = os.getenv("EMAIL_HOST_USER")
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=from_email,
        to=[to_email],
    )
    email.attach_alternative(html_message, "text/html")
    
    img_path = os.path.join(settings.BASE_DIR, "auth_app",
                            "static", "auth_app", "images", "Logo.png")
    with open(img_path, "rb") as f:
        img = MIMEImage(f.read())
        img.add_header("Content-ID", "<logo>")
        img.add_header("Content-Disposition", "inline", filename="Logo.png")
        email.attach(img)

    email.send()


def send_password_reset_mail(user):
    """
    Enqueues the styled password reset email via Django-RQ.
    """
    reset_url = (
        f"http://127.0.0.1:5500/pages/auth/confirm_password.html"
        f"?uid={urlsafe_base64_encode(force_bytes(user.pk))}"
        f"&token={account_activation_token.make_token(user)}"
    )
    queue = django_rq.get_queue("default", autocommit=True)
    queue.enqueue(do_send_password_reset, user.email, reset_url)
