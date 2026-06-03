from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """DRF exception handler that converts Django's ProtectedError
    (raised on delete of an object still referenced via on_delete=PROTECT)
    into a 409 Conflict instead of an unhandled 500.
    """
    response = exception_handler(exc, context)
    if response is None and isinstance(exc, ProtectedError):
        return Response(
            {
                "detail": (
                    "Cannot delete this object because it is referenced "
                    "by other records."
                )
            },
            status=status.HTTP_409_CONFLICT,
        )
    return response
