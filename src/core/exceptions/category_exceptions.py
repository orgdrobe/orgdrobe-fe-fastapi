from core.enums import ErrorCode
from core.exceptions.base_exception import BaseAPIException


class CategoryMasterNotFound(BaseAPIException):
    status_code = 404
    code = ErrorCode.CATEGORY_MASTER_NOT_FOUND
    def __init__(self, id: int):
        super().__init__(
            message=f"CategoryMaster with id {id} not found"
        )