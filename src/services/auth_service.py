
from schemas.user import UserRegister, UserOut
from repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository 

    def register_user(self, new_user: UserRegister) -> UserOut: 
        return UserOut()