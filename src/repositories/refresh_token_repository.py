from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import RefreshToken

class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, refresh_token: RefreshToken) -> RefreshToken:
        self._session.add(refresh_token)
        await self._session.flush()
        await self._session.refresh(refresh_token)
        return refresh_token