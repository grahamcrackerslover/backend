from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


def InvalidArgumentsHandler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, (KeyError, ValidationError, TypeError)):
        return Response(
            {"error": "Invalid arguments"}, status=status.HTTP_400_BAD_REQUEST
        )
    return response
