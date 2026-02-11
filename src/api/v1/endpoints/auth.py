from fastapi import APIRouter, Depends

from schemas.user import UserRegister, UserOut
from schemas.errors import ErrorResponse
from dependencies.auth_service import get_auth_service
from services.interfaces import AuthServiceInterface

router = APIRouter()


@router.post("/register", 
    response_model=UserOut,
    status_code=201,
    responses={
        409: {"model": ErrorResponse, "description": "Username already exist"}
    }
)
async def register(payload: UserRegister, auth_service: AuthServiceInterface = Depends(get_auth_service)) -> UserOut:
    result = await auth_service.register_user(payload)
    return result

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