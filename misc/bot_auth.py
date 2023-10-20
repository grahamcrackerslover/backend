from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from backend.settings import ALLOWED_BOT_TOKENS


class BotTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION") or request.META.get(
            "Authorization"
        )

        if not auth_header or not auth_header.startswith("Bot "):
            return None

        token = auth_header.split()[1]
        if token in ALLOWED_BOT_TOKENS.keys():
            return ALLOWED_BOT_TOKENS[token], token
        else:
            raise exceptions.AuthenticationFailed("Invalid token")
