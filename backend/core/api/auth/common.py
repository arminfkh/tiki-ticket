import json

from django.http import JsonResponse


def error_response(
    code: str,
    message: str,
    *,
    status: int = 400,
) -> JsonResponse:
    """
    make all API errors have one consistent JSON format
    """
    return JsonResponse(
        {
            "error": {
                "code": code,
                "message": message,
            }
        },
        status=status,
    )


def get_required_text(
    data: dict,
    field_name: str,
) -> str:
    """
    Get this required field,
    make sure it's a string, trim whitespace,
    and reject it if empty.
    """
    value = data.get(field_name)

    if not isinstance(value, str):
        raise ValueError(f"The {field_name} field is required.")

    value = value.strip()

    if not value:
        raise ValueError(f"The {field_name} field cannot be empty.")

    return value


def read_json_object(request) -> dict:
    """
    Read a JSON object from the request body.
    """
    try:
        data = json.loads(request.body)
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ) as exc:
        raise ValueError("The request body must contain valid JSON.") from exc

    if not isinstance(data, dict):
        raise ValueError("The JSON request body must be an object.")

    return data
