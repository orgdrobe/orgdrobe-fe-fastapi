from fastapi import APIRouter, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm

from core.configs.jwt_config import jwt_config
from schemas.user import UserRegister, UserRegisterOut, UserLogin, UserLoginOut
from schemas.errors import ErrorResponse
from dependencies.auth_service import get_auth_service
from dependencies.security import get_current_user, require_role
from services.interfaces import AuthServiceInterface
from models import User

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
async def local_login(response: Response, payload: OAuth2PasswordRequestForm = Depends(), auth_service: AuthServiceInterface = Depends(get_auth_service)) -> UserLoginOut:
    login_result, refresh_token  = await auth_service.local_login(UserLogin(email=payload.username, password=payload.password))
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True, # Dev = False
        samesite="lax", 
        max_age=jwt_config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    return login_result


# TEST ROUTE
@router.get("/me", response_model=dict)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return {"message": f"{current_user.username}"}

@router.get("/admin", response_model=dict)
async def read_role_user(
    current_user: User = Depends(require_role(["admin"]))
):
    return {"message": f"you are user!"}

#class TransactionContext()
#   def rollback()
#   def commit()

# @router.post("/login", response_model=TempData)
# async def login(db: TempData, credentials: TempData):
#     return None

# @router.post("/google", response_model=TempData)
# async def google(db: TempData, credentials: TempData):
#     return None