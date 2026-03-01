from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.views import (TokenObtainPairView, 
                                            TokenRefreshView)
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegistrationSerializer, CustomTokenObtainPairSerializer
from .utils import account_activation_token
from .permissions import HasRefreshToken


class RegistrationAPIView(APIView):
    """
    View for registering user. The return statement has no usage for the frontend.
    It is only useful for seeing the status.
    Make sure to also check out the signals.py method. 
    There will be a email send out to the user, for activating his account.
    """
    permission_classes = [AllowAny]

    def post(self, req):
        serializer = RegistrationSerializer(data=req.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return Response({
                "user": {
                    "id": data.pk,
                    "email": data.email
                },
                "token": "activation_token"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountActivationView(APIView):
    """
    This view is for activating the user account. 
    When the user registers a neww account, it is not active by default.
    The user has to go into his email account, and click on the activation link.
    This link will trigger this view.
    """
    permission_classes = [AllowAny]

    def get(self, req, uidb64, token):
        """
        Validates the base64 encoded User pk and the created token.
        If boths values are valid, the user is_active status will be set to True.
        After that, the user is able to log his account in.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Activation not successful. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )
        

class LoginView(TokenObtainPairView):
    """
    This view is for logging in a user.
    """
    permission_classes = [AllowAny]

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        Validates the email and password. After that it log's the user in and
        return the access and refresh token as HTTP Cookies.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]
        response = Response({"message": "Login erfolgreich"})

        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=True,
            samesite="Lax"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return response
    

class LogoutView(APIView):
    """
    This view is for logging a user out.
    """
    permission_classes = [IsAuthenticated, HasRefreshToken]

    def post(self, request):
        """
        Deletes the access and refresh token from the response cookie.
        Sets the refresh token on a blacklist, so it can't be reused.
        User has to re enter his initials if he wants to continue.
        """
        refresh_token = RefreshToken(request.COOKIES.get("refresh_token"))
        refresh_token.blacklist()
        response = Response(
            {
                "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
            }
        )
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response


class RefreshView(TokenRefreshView):
    """
    With the help of this view are users able, to refresh their access token without
    the need to login again.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        If the access token has expired, the user can claim another one.
        With the help of this view, it makes use of the refresh token. 
        If it is valid, the view will return a new access token via the response cookie.
        """
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                {"detail": "Refresh token invalid"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        access_token = serializer.validated_data.get("access")
        response = Response(
            {
                "detail": "Token refreshed",
                "access": "new_access_token"
            }
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return response


