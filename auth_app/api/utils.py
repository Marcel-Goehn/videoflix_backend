import os
import six

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import get_connection
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import django_rq

from dotenv import load_dotenv


load_dotenv()


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Creates a unique token to verify email requests.
    """
    def _make_hash_value(self, user, timestamp):
        return(
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()


def send_activation_email(to_email, username, activation_url):
    """
    Sends an email after registration to activate the user
    """
    logo_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', 'static', 'auth_app', 'images', 'Logo.png')
    )
    context = {
        "username": username,
        "activation_url": activation_url,
        "logo_url": "cid:logo_image",
    }
    html_message = render_to_string("auth_app/activation_email.html", context)
    plain_message = (
        f"Dear {username},\n\n"
        "Thank you for registering with Videoflix. To activate your account visit:\n"
        f"{activation_url}\n\n"
        "If you did not create an account, please disregard this email.\n\n"
        "Best regards,\nYour Videoflix Team."
    )
    from_email = os.environ.get("EMAIL_HOST_USER")

    msg = MIMEMultipart('related')
    msg['Subject'] = "Confirm your email"
    msg['From'] = from_email
    msg['To'] = to_email

    msg_alt = MIMEMultipart('alternative')
    msg_alt.attach(MIMEText(plain_message, 'plain', 'utf-8'))
    msg_alt.attach(MIMEText(html_message, 'html', 'utf-8'))
    msg.attach(msg_alt)

    with open(logo_path, 'rb') as f:
        logo = MIMEImage(f.read())
    logo.add_header('Content-ID', '<logo_image>')
    logo.add_header('Content-Disposition', 'inline', filename='Logo.png')
    msg.attach(logo)

    connection = get_connection(fail_silently=False)
    connection.open()
    connection.connection.sendmail(from_email, [to_email], msg.as_bytes())
    connection.close()


def do_send_password_reset(to_email, reset_url):
    """
    Sends an email to verify that the password reset request is really coming
    from the actual user
    """
    logo_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', 'static', 'auth_app', 'images', 'Logo.png')
    )
    context = {
        "reset_url": reset_url,
        "logo_url": "cid:logo_image",
    }
    html_message = render_to_string("auth_app/password_reset_email.html", context)
    plain_message = (
        "Hello,\n\n"
        "We recently received a request to reset your password. "
        "If you made this request, please visit:\n"
        f"{reset_url}\n\n"
        "Please note that for security reasons, this link is only valid for 24 hours.\n\n"
        "If you did not request a password reset, please ignore this email.\n\n"
        "Best regards,\nYour Videoflix team!"
    )
    from_email = os.environ.get("EMAIL_HOST_USER")

    msg = MIMEMultipart('related')
    msg['Subject'] = "Reset your Password"
    msg['From'] = from_email
    msg['To'] = to_email

    msg_alt = MIMEMultipart('alternative')
    msg_alt.attach(MIMEText(plain_message, 'plain', 'utf-8'))
    msg_alt.attach(MIMEText(html_message, 'html', 'utf-8'))
    msg.attach(msg_alt)

    with open(logo_path, 'rb') as f:
        logo = MIMEImage(f.read())
    logo.add_header('Content-ID', '<logo_image>')
    logo.add_header('Content-Disposition', 'inline', filename='Logo.png')
    msg.attach(logo)

    connection = get_connection(fail_silently=False)
    connection.open()
    connection.connection.sendmail(from_email, [to_email], msg.as_bytes())
    connection.close()


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
