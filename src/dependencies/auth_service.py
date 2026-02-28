from fastapi import Depends
from passlib.context import CryptContext

from services import AuthService
from services.interfaces import AuthServiceInterface, UnitOfWorkInterface
from .unit_of_work import get_unit_of_work
from .password_context import get_pwd_context

def get_auth_service(uow: UnitOfWorkInterface = Depends(get_unit_of_work), pwd_context: CryptContext = Depends(get_pwd_context)) -> AuthServiceInterface: 
    return AuthService(uow, pwd_context)