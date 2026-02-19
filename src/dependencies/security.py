from typing import Callable

import jwt
from jwt.exceptions import PyJWTError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from core.configs.jwt_config import jwt_config
from core.exceptions.auth_exceptions import MissingAccessToken, InvalidAccessPayload, InvalidAccessToken, AccessUserNotFound, InsufficientRole
from dependencies.unit_of_work import get_unit_of_work
from services.interfaces import UnitOfWorkInterface
from repositories import UserRepository
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme), 
        uow: UnitOfWorkInterface = Depends(get_unit_of_work)
        ) -> User:
    try:
        payload = jwt.decode(token, jwt_config.SECRET_KEY, algorithms=[jwt_config.ALGORITHM])
        if payload.get("type") != "access":
            raise MissingAccessToken()
        
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise InvalidAccessPayload()
        
        user_id = int(user_id_str) 
        
    except PyJWTError as e:
        # print(f"Error JWT: {type(e).__name__} - {str(e)}")
        raise InvalidAccessToken()
    
    async with uow:
        user_repo = uow.get_repo(UserRepository)
         
        # TODO: add roles get in repo
        user = await user_repo.get_by_id_with_roles(user_id)
        
        if user is None:
            raise AccessUserNotFound()
        
    return user

def require_role(required_roles: list[str]) -> Callable[[User],User]:
    def dependency(user: User = Depends(get_current_user)) -> User:
        user_roles = [role.name for role in user.roles]
        if not all(role in user_roles for role in required_roles):
            raise InsufficientRole()
        return user
    return dependency