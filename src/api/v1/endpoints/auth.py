from fastapi import APIRouter, Response, Depends

from core.configs.jwt_config import jwt_config
from schemas.user import UserRegister, UserRegisterOut, UserLogin, UserLoginOut
from schemas.errors import ErrorResponse
from dependencies.auth_service import get_auth_service
from services.interfaces import AuthServiceInterface

router = APIRouter()

@router.post("/register", 
    response_model=UserRegisterOut,
    status_code=201,
    responses={
        409: {"model": ErrorResponse, "description": "Username already exist"} # TODO: extend for all in method
    }
)
async def register(payload: UserRegister, auth_service: AuthServiceInterface = Depends(get_auth_service)) -> UserRegisterOut:
    result = await auth_service.register_user(payload)
    return result



@router.post("/login", 
    response_model=UserLoginOut,
    status_code=200,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid username or password."} # TODO: extend for all in method
    }
)
async def local_login(payload: UserLogin, response: Response, auth_service: AuthServiceInterface = Depends(get_auth_service)) -> UserLoginOut:
    login_result, refresh_token  = await auth_service.local_login(payload)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True, # Dev = False
        samesite="lax", 
        max_age=jwt_config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    return login_result


#class TransactionContext()
#   def rollback()
#   def commit()

# @router.post("/login", response_model=TempData)
# async def login(db: TempData, credentials: TempData):
#     return None

# @router.post("/google", response_model=TempData)
# async def google(db: TempData, credentials: TempData):
#     return None