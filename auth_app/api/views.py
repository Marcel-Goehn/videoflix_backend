from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, inline_serializer
from rest_framework import serializers

from .serializers import (RegistrationSerializer, CustomTokenObtainPairSerializer,
                          PasswordResetSerializer, NewPasswordSerializer)
from .utils import account_activation_token, send_password_reset_mail


@extend_schema(
    request=inline_serializer(
        name='RegistrationRequest',
        fields={
            'email': serializers.EmailField(),
            'password': serializers.CharField(),
            'confirmed_password': serializers.CharField(),
        }
    ),
    responses={
        201: inline_serializer(
            name='RegistrationResponse',
            fields={
                'user': inline_serializer(
                    name='RegistrationUserData',
                    fields={
                        'id': serializers.IntegerField(),
                        'email': serializers.EmailField(),
                    }
                ),
                'token': serializers.CharField(),
            }
        ),
        400: OpenApiResponse(description='Validation error'),
    },
    summary='Register a new user',
    tags=['Auth'],
)
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


@extend_schema(
    parameters=[
        OpenApiParameter('uidb64', str, OpenApiParameter.PATH, description='Base64-encoded user ID'),
        OpenApiParameter('token', str, OpenApiParameter.PATH, description='Account activation token'),
    ],
    responses={
        200: OpenApiResponse(description='Account successfully activated'),
        400: OpenApiResponse(description='Invalid or expired activation link'),
    },
    summary='Activate account via email link',
    tags=['Auth'],
)
class AccountActivationView(APIView):
    """
    This view is for activating the user account.
    When the user registers a new account, it is not active by default.
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
        

@extend_schema(
    request=CustomTokenObtainPairSerializer,
    responses={
        200: OpenApiResponse(description='Sets access_token and refresh_token cookies'),
        400: OpenApiResponse(description='Invalid Email or password')
    },
    summary='Login and receive JWT cookies',
    tags=['Auth'],
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
    

@extend_schema(
    request=None,
    responses={
        200: OpenApiResponse(description='Clears JWT cookies and blacklists refresh token'),
        400: OpenApiResponse(description='Refresh token not found in cookies')
    },
    summary='Logout and invalidate tokens',
    description='Requires a valid `access_token` and `refresh_token` cookie. No request body needed.',
    tags=['Auth'],
)
class LogoutView(TokenRefreshView):
    """
    This view is for logging a user out.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Deletes the access and refresh token from the response cookie.
        Sets the refresh token on a blacklist, so it can't be reused.
        User has to re enter his initials if he wants to continue.
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

        refresh_token_blacklist = RefreshToken(refresh_token)
        refresh_token_blacklist.blacklist()
        response = Response(
            {
                "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
            }
        )
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response


@extend_schema(
    request=None,
    responses={
        200: OpenApiResponse(description='Issues new access_token cookie'),
        400: OpenApiResponse(description='Refresh token is missing'),
        401: OpenApiResponse(description='Invalid refresh token')
    },
    summary='Refresh access token via cookie',
    tags=['Auth'],
)
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


@extend_schema(
    request=PasswordResetSerializer,
    responses={
        200: OpenApiResponse(description='Password reset email sent'),
        404: OpenApiResponse(description='User with that email not found'),
    },
    summary='Request password reset email',
    tags=['Auth'],
)
class PasswordResetView(APIView):
    """
    This view sends out an email to reset the users password
    """
    permission_classes = [AllowAny]

    def post(self, req):
        """
        Calls the send_password_reset_mail() function. It is sending out an email with DjangoRQ,
        so that the users has not to wait until the mail is send.
        """
        serializer = PasswordResetSerializer(data=req.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data
            user = User.objects.get(email=data["email"])
            send_password_reset_mail(user)
            return Response({"detail": "An email has been sent to reset your password."})
        return Response(serializer.errors)
    

@extend_schema(
    request=NewPasswordSerializer,
    parameters=[
        OpenApiParameter('uidb64', str, OpenApiParameter.PATH, description='Base64-encoded user ID'),
        OpenApiParameter('token', str, OpenApiParameter.PATH, description='Password reset token'),
    ],
    responses={
        200: OpenApiResponse(description='Password successfully reset'),
        400: OpenApiResponse(description='Invalid or expired reset token / Passwords do not match')
    },
    summary='Set new password via reset link',
    tags=['Auth'],
)
class NewPasswordView(APIView):
    """
    Updates the users password after receiving a reset link via email.
    """
    permission_classes = [AllowAny]

    def post(self, req, uidb64, token):
        """
        Retrieves the user id wich is encoded in base64.
        Also retrieves a token to verify the request.
        This view decodes the token and user id. If bot are valid,
        the newly entered password will be hashed and saved to the database.
        """
        serializer = NewPasswordSerializer(data=req.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data
            new_password = data["new_password"]
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            if user is not None and account_activation_token.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response(
                    {"detail": "Your Password has been successfully reset."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "Your reset token expired. Please request a new reset mail."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


