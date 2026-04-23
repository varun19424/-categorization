from rest_framework import status
from rest_framework.exceptions import APIException


class ApiError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "bad_request"
    default_detail = "Request could not be processed."

    def __init__(self, detail=None, code=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail=detail or self.default_detail, code=code or self.default_code)

    def get_full_details(self):
        details = super().get_full_details()
        return {
            "error": {
                "code": details["code"],
                "message": details["message"],
            }
        }


class UnknownCompanyError(ApiError):
    default_code = "unknown_company"
    default_detail = "Company context was not found."


class ProviderConfigurationError(ApiError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = "provider_configuration_error"
    default_detail = "LLM provider configuration is incomplete."


class StructuredOutputError(ApiError):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_code = "invalid_provider_response"
    default_detail = "Provider response did not match the expected schema."
