from django.urls import path
from .views import RegistrationAPIView, AccountActivationView

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("activate/<str:uidb64>/<str:token>/", AccountActivationView.as_view(), name="activate")
]