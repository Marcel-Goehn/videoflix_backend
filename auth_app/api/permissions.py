from rest_framework.permissions import BasePermission


class HasRefreshToken(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token is not None:
                return True
            else:
                return False