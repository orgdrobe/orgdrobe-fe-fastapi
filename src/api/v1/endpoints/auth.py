from fastapi import APIRouter

from schemas.user import UserRegister, UserOut
from schemas.errors import ErrorResponse
from core.exceptions.api_exceptions import UsernameAlreadyExists

router = APIRouter()


@router.post("/register", 
    response_model=UserOut,
    responses={
        409: {"model": ErrorResponse, "description": "Username already exist"}
    }
)
async def register(payload: UserRegister) -> UserOut:
        # raise UsernameAlreadyExists("admin")
        # raise NotImplementedError()
    return UserOut()

# Додай контекст наприклад 
#class TransactionContext()
#   def rollback()
#   def commit()

# @router.post("/login", response_model=TempData)
# async def login(db: TempData, credentials: TempData):
#     return None

# @router.post("/google", response_model=TempData)
# async def google(db: TempData, credentials: TempData):
#     return None