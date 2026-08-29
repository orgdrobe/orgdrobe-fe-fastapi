from core.enums import ErrorCode
from core.exceptions.base_exception import BaseAPIException


class OutfitNotFound(BaseAPIException):
    status_code = 404
    code = ErrorCode.OUTFIT_NOT_FOUND
    def __init__(self, id: int):
        super().__init__(
            message=f"Outfit with id {id} not found"
        )

