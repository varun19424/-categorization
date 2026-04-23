from rest_framework.views import exception_handler


def _collect_required_fields(data, prefix=""):
    missing = []
    if isinstance(data, dict):
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, list) and any(str(item) == "This field is required." for item in value):
                missing.append(key)
            else:
                missing.extend(_collect_required_fields(value, path))
    elif isinstance(data, list):
        for item in data:
            missing.extend(_collect_required_fields(item, prefix))
    return missing


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    detail = response.data.get("detail") if isinstance(response.data, dict) else None
    if isinstance(response.data, dict) and detail is None:
        missing_fields = _collect_required_fields(response.data)
        if missing_fields:
            normalized = set(missing_fields)
            if "description" in normalized and "chart_of_accounts" in normalized:
                response.data = {
                    "error": "Invalid input: description and chart_of_accounts are required"
                }
                return response
            if "description" in normalized:
                response.data = {"error": "Invalid input: description is required"}
                return response
            if "chart_of_accounts" in normalized:
                response.data = {"error": "Invalid input: chart_of_accounts is required"}
                return response

            response.data = {
                "error": "Invalid input"
            }
            return response

        company_context_errors = response.data.get("company_context", {})
        chart_errors = company_context_errors.get("chart_of_accounts", [])
        if "Chart of accounts cannot be empty" in chart_errors:
            response.data = {"error": "Chart of accounts cannot be empty"}
            return response

        response.data = {
            "error": "Invalid input"
        }
        return response

    if isinstance(detail, dict):
        message = detail.get("message", "Request could not be processed.")
        code = detail.get("code", "bad_request")
    else:
        message = str(detail or "Request could not be processed.")
        code = getattr(exc, "default_code", "bad_request")

    response.data = {"error": message}
    return response
