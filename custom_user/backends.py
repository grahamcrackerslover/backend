# backends.py
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import CustomUser


class TelegramTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION") or request.META.get(
            "Authorization"
        )

        if not auth_header or not auth_header.startswith("KWT "):
            return None

        token = auth_header.split()[1]
        user = self.get_user_from_token(token)

        if user:
            if user.is_banned:
                raise exceptions.AuthenticationFailed("User is banned")
            print(f"Authenticated user: {user}, token: {token}")

            user.current_ip = request.META.get("REMOTE_ADDR")
            return (
                user,
                token,
            )  # Return a tuple containing the user object and the authentication token
        else:
            raise exceptions.AuthenticationFailed(
                "Invalid token"
            )  # Raise an exception if token is invalid

    def get_user_from_token(self, token):
        try:
            user = CustomUser.objects.get(token=token)
            return user
        except CustomUser.DoesNotExist:
            return None
