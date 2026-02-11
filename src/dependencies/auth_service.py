from fastapi import Depends

from services.auth_service import AuthService
from services.interfaces import AuthServiceInterface, UnitOfWorkInterface
from dependencies.unit_of_work import get_unit_of_work

def get_auth_service(uow: UnitOfWorkInterface = Depends(get_unit_of_work)) -> AuthServiceInterface: 
    return AuthService(uow)