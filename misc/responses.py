from rest_framework import status
from rest_framework.response import Response


def success_response(heading, message, data, code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "heading": heading,
        "message": message,
        "data": data
    }, status=code)


def error_response(heading, message, errors, code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "heading": heading,
        "message": message,
        "errors": errors
    }, status=code)


