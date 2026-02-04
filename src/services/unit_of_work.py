from typing import Callable, TypeVar, Optional, Type, Any, Self
from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from .interfaces import UnitOfWorkInterface

R = TypeVar("R")

class SqlAlchemyUnitOfWork(UnitOfWorkInterface):
    
    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None

        self._repositories: dict[Type[Any], Any] = {}
        self._factories: dict[Type[Any], Callable[[AsyncSession], Any]] = {}

    def register_factory(self, repo_type: Type[R], factory: Callable[[AsyncSession], R]) -> None:
        self._factories[repo_type] = factory

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        return self
    
    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        if not self._session:
            return
    
        try:
            if exc_type:
                await self.rollback()
            else:
                # can be explicit commit if we need
                # await self.commit()
                pass
        finally:
            await self._session.close()
            self._session = None
            self._repositories = {}
        
    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()
     
    def get_repo(self, repo_type: Type[R]) -> R:
        if self._session is None:
            raise RuntimeError("Unit of Work has not been started. Use async with uow:")
        
        if repo_type in self._repositories:
            return self._repositories[repo_type]
        
        if repo_type not in self._factories:
            raise KeyError(f"Factory for repository '{repo_type.__name__}' is not registered.")
        
        factory = self._factories[repo_type]
        new_repo = factory(self._session)
        self._repositories[repo_type] = new_repo

        return new_repo

