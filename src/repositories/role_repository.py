from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Optional

from models import Role 

class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_role_by_name(self, role_name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.name == role_name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()