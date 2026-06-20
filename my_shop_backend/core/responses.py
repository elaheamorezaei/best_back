from rest_framework.response import Response


# ─── Homepage-style responses ────────────────────────────────────────────────

def success_response(data, status=200):
    return Response({"success": True, "data": data}, status=status)


def not_found_response(message="Not found"):
    return Response({"success": False, "message": message}, status=404)


def error_response(message="Bad request", status=400):
    return Response({"success": False, "message": message}, status=status)


# ─── Product-page-style responses ────────────────────────────────────────────

def data_response(data, message="", status=200):
    result = {"data": data}
    if message:
        result["message"] = message
    return Response(result, status=status)


def error_detail_response(code, message, field=None, http_status=400):
    err = {"code": code, "message": message}
    if field:
        err["field"] = field
    return Response({"error": err}, status=http_status)


# ─── Image URL helper ─────────────────────────────────────────────────────────

def build_absolute_image_url(request, image_field):
    if not image_field:
        return None
    try:
        return request.build_absolute_uri(image_field.url)
    except (ValueError, AttributeError):
        return None
