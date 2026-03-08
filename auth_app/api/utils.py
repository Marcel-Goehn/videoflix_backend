import os
import six

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

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


def send_password_reset_mail(user):
    """
    Puts the password reset mail into the DjangoRQ, so that the user doesn't need to wait.
    """
    queue = django_rq.get_queue("default", autocommit=True)
    queue.enqueue(send_mail,
                  "Reset your password",
                  f"""Hello,

                   We recently received a request to reset your password. If you made this request, please click on the following link to reset your password:

                   http://127.0.0.1:5500/pages/auth/confirm_password.html?uid={urlsafe_base64_encode(force_bytes(user.pk))}&token={account_activation_token.make_token(user)}

                   Please note that, for security reasons, this link is only valid for 24 hours.

                   If you did not request a password reset, please ignore this email.

                   Best regards,

                   Your Videoflix team!""",
                   os.environ.get("EMAIL_HOST_USER"),
                   [user.email],
                   fail_silently=False)
