from abc import ABC, abstractmethod

from schemas.user import UserRegister, UserRegisterOut, UserLogin, UserLoginOut

class AuthServiceInterface(ABC):
    @abstractmethod
    async def register_user(self, new_user: UserRegister) -> UserRegisterOut: ...

    @abstractmethod
    async def local_login(self, user_credentials: UserLogin) -> tuple[UserLoginOut, str]: ...

    @abstractmethod
    async def refresh_tokens(self, refresh_token: str | None) -> tuple[UserLoginOut, str]: ... 

    @abstractmethod
    async def logout(self, refresh_token: str | None) -> None: ...