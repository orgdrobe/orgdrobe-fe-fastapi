from core.enums.error_codes import ErrorCode
from core.exceptions.base_exception import BaseAPIException

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
    headers={"WWW-Authenticate": "Bearer"}

class InvalidRefreshToken(BaseAPIException):
    status_code = 401
    code = ErrorCode.REFRESH_TOKEN_INVALID
    message = "Invalid refresh token."
    headers={"WWW-Authenticate": "Bearer"}

class InvalidRefreshPayload(BaseAPIException):
    status_code = 401
    code = ErrorCode.REFRESH_TOKEN_PAYLOAD_INVALID
    message = "Invalid refresh payload."
    headers={"WWW-Authenticate": "Bearer"}

class RefreshTokenRevokedOrExpired(BaseAPIException):
    status_code = 401
    code = ErrorCode.REFRESH_TOKEN_EXPIRED
    message = "Refresh token revoked or expired."
    headers={"WWW-Authenticate": "Bearer"}

class RefreshUserNotFound(BaseAPIException):
    status_code = 401
    code = ErrorCode.REFRESH_USER_NOT_FOUND
    message = "User associated with this token no longer exists."
    headers={"WWW-Authenticate": "Bearer"}


# --- Access Token Errors (Dependencies) ---

class MissingAccessToken(BaseAPIException):
    status_code = 401
    code = ErrorCode.ACCESS_TOKEN_MISSING
    message = "Missing access token in Authorization header."
    headers={"WWW-Authenticate": "Bearer"}

class InvalidAccessToken(BaseAPIException):
    status_code = 401
    code = ErrorCode.ACCESS_TOKEN_INVALID
    message = "Invalid access token."
    headers={"WWW-Authenticate": "Bearer"}

class InvalidAccessPayload(BaseAPIException):
    status_code = 401
    code = ErrorCode.ACCESS_TOKEN_PAYLOAD_INVALID
    message = "Invalid access token payload."
    headers={"WWW-Authenticate": "Bearer"}

class AccessUserNotFound(BaseAPIException):
    status_code = 401
    code = ErrorCode.ACCESS_USER_NOT_FOUND
    message = "User associated with this token not found."
    headers={"WWW-Authenticate": "Bearer"}

# --- Permissions ---

class InsufficientRole(BaseAPIException):
    status_code = 403
    code = ErrorCode.INSUFFICIENT_PERMISSIONS
    message = "You do not have the required role to perform this action."