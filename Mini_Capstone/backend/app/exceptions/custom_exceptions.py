"""Custom exception types for the API."""


class AppException(Exception):
    status_code = 400
    detail = "Application error."

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail or self.detail)
        self.detail = detail or self.detail


class ValidationException(AppException):
    status_code = 422
    detail = "Validation failed."


class UnauthorizedException(AppException):
    status_code = 401
    detail = "Authentication required."


class ForbiddenException(AppException):
    status_code = 403
    detail = "You do not have permission to perform this action."


class NotFoundException(AppException):
    status_code = 404
    detail = "Requested resource was not found."


class ConflictException(AppException):
    status_code = 409
    detail = "Resource already exists."
