from typing import Optional, Any
from core.enums.error_codes import ErrorCode

class BaseAPIException(Exception):
    status_code: int = 500
    code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR
    message: str = "An unexpected error occurred."

    def __init__(self, message: Optional[str] = None, details: Optional[Any] = None) -> None:
        if message:
            self.message = message
        self.details = details
        super().__init__(self.message)


# --- Registration & Login ---

class UsernameAlreadyExists(BaseAPIException):
    status_code = 409
    code = ErrorCode.USERNAME_TAKEN
    message = "Username already exists."

    def __init__(self, username: str):
        super().__init__(
            message=f"Username '{username}' already exists",
            details={"field": "username", "value": username}
        )

class EmailAlreadyExists(BaseAPIException):
    status_code = 409
    code = ErrorCode.EMAIL_TAKEN
    message = "Email already exists."

    def __init__(self, email: str):
        super().__init__(
            message=f"Email '{email}' already exists",
            details={"field": "email", "value": email}
        )

class InvalidCredentials(BaseAPIException):
    status_code = 401
    code = ErrorCode.INVALID_CREDENTIALS
    message = "Invalid username or password."


# --- Refresh Token Errors ---

class MissingRefreshToken(BaseAPIException):
    status_code = 401
    code = ErrorCode.REFRESH_TOKEN_MISSING
    message = "Missing refresh token cookie."

class InvalidRefreshToken(BaseAPIException):
    status_code = 401
    code = ErrorCode.REFRESH_TOKEN_INVALID
    message = "Invalid refresh token."

class InvalidRefreshPayload(BaseAPIException):
    status_code = 401
    code = ErrorCode.REFRESH_TOKEN_PAYLOAD_INVALID
    message = "Invalid refresh payload."

class RefreshTokenRevokedOrExpired(BaseAPIException):
    status_code = 401
    code = ErrorCode.REFRESH_TOKEN_EXPIRED
    message = "Refresh token revoked or expired."

class RefreshUserNotFound(BaseAPIException):
    status_code = 401
    code = ErrorCode.REFRESH_USER_NOT_FOUND
    message = "User associated with this token no longer exists."


# --- Access Token Errors (Dependencies) ---

class MissingAccessToken(BaseAPIException):
    status_code = 401
    code = ErrorCode.ACCESS_TOKEN_MISSING
    message = "Missing access token in Authorization header."

class InvalidAccessToken(BaseAPIException):
    status_code = 401
    code = ErrorCode.ACCESS_TOKEN_INVALID
    message = "Invalid access token."

class InvalidAccessPayload(BaseAPIException):
    status_code = 401
    code = ErrorCode.ACCESS_TOKEN_PAYLOAD_INVALID
    message = "Invalid access token payload."

class AccessUserNotFound(BaseAPIException):
    status_code = 401
    code = ErrorCode.ACCESS_USER_NOT_FOUND
    message = "User associated with this token not found."


# --- Permissions ---

class InsufficientRole(BaseAPIException):
    status_code = 403
    code = ErrorCode.INSUFFICIENT_PERMISSIONS
    message = "You do not have the required role to perform this action."