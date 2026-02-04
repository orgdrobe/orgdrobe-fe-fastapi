
from schemas.user import UserRegister, UserOut
from services.unit_of_work import UnitOfWorkInterface

class AuthService:
    def __init__(self, uow: UnitOfWorkInterface) -> None:
        self._uow = uow 

    def register_user(self, new_user: UserRegister) -> UserOut: 
        return UserOut()