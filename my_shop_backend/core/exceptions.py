from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    code = response.status_code
    data = response.data

    # Extract message from DRF's response data
    if isinstance(data, dict):
        if 'detail' in data:
            message = str(data['detail'])
        else:
            # Validation errors: pick first field's first message
            first_field = next(iter(data))
            first_errors = data[first_field]
            if isinstance(first_errors, list):
                message = str(first_errors[0])
            else:
                message = str(first_errors)
            return Response(
                {"error": {"code": code, "message": message, "field": first_field}},
                status=code
            )
    else:
        message = str(data)

    return Response(
        {"error": {"code": code, "message": message}},
        status=code
    )
