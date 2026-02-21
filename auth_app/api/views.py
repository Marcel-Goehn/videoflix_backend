from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# from rest_framework_simplejwt.views import (TokenObtainPairView, 
#                                             TokenRefreshView)

from .serializers import RegistrationSerializer


class RegistrationAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, req):
        serializer = RegistrationSerializer(data=req.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            print(data)
            return Response({
                "user": {
                    "id": data.pk,
                    "email": data.email
                },
                "token": "activation_token"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

