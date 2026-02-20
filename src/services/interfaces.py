from abc import ABC, abstractmethod
from typing import Type, TypeVar, Self

from schemas.user import UserRegister, UserRegisterOut, UserLogin, UserLoginOut

R = TypeVar("R")

class UnitOfWorkInterface(ABC):
    @abstractmethod
    async def __aenter__(self) -> Self: ...
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...
    
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    def get_repo(self, repo_type: Type[R]) -> R: ...


class AuthServiceInterface(ABC):
    @abstractmethod
    async def register_user(self, new_user: UserRegister) -> UserRegisterOut: ...

    @abstractmethod
    async def local_login(self, user_credentials: UserLogin) -> tuple[UserLoginOut, str]: ...

    @abstractmethod
    async def refresh_tokens(self, refresh_token: str | None) -> tuple[UserLoginOut, str]: ... 

    @abstractmethod
    async def logout(self, refresh_token: str | None) -> None: ...