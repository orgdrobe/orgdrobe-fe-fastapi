from fastapi import Depends
from passlib.context import CryptContext

from services.auth_service import AuthService
from services.interfaces import AuthServiceInterface, UnitOfWorkInterface
from dependencies.unit_of_work import get_unit_of_work
from dependencies.password_context import get_pwd_context

def get_auth_service(uow: UnitOfWorkInterface = Depends(get_unit_of_work), pwd_context: CryptContext = Depends(get_pwd_context)) -> AuthServiceInterface: 
    return AuthService(uow, pwd_context)