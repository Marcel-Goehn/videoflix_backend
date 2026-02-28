from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# from rest_framework_simplejwt.views import (TokenObtainPairView, 
#                                             TokenRefreshView)

from .serializers import RegistrationSerializer
from .utils import account_activation_token


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
    permission_classes = [AllowAny]

    def get(self, req, uidb64, token):
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
