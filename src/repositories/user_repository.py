from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_user(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user
    
    