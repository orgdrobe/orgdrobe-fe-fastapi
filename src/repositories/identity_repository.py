from sqlalchemy.ext.asyncio import AsyncSession

from models import UserIdentity

class UserIdentityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_user_identity(self, user_identity: UserIdentity) -> UserIdentity:
        self._session.add(user_identity)
        await self._session.flush()
        await self._session.refresh(user_identity)
        return user_identity