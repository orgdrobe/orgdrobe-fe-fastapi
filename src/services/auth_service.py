
from schemas.user import UserRegister, UserOut
from services.unit_of_work import UnitOfWorkInterface
from services.interfaces import AuthServiceInterface

class AuthService(AuthServiceInterface):
    def __init__(self, uow: UnitOfWorkInterface) -> None:
        self._uow = uow 

    def register_user(self, new_user: UserRegister) -> UserOut: 
        # TODO
        user = None
        return UserOut.model_validate(user)