from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom authenticate method. This has to be done, because in this project
    are http only cookies used to authenticate. The standard drf JWT authentication class 
    only works with request headers, not cookies.
    """
    def authenticate(self, request):
        token = request.COOKIES.get("access_token")
        if not token:
            return None

        try:
            validated_token = self.get_validated_token(token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except (InvalidToken, TokenError, AuthenticationFailed):
            return None
