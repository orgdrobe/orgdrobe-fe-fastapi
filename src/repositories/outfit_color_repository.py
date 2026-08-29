from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.interfaces import OutfitColorRepositoryInterface
from models import OutfitColor


class OutfitColorRepository(OutfitColorRepositoryInterface):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, outfit_color: OutfitColor) -> OutfitColor:
        self._session.add(outfit_color)
        await self._session.flush()
        await self._session.refresh(outfit_color)
        return outfit_color

    async def add_range(self, outfit_color_range: list[OutfitColor]) -> list[OutfitColor]:
        self._session.add_all(outfit_color_range)
        await self._session.flush()
        for oc in outfit_color_range:
            await self._session.refresh(oc)
        return outfit_color_range

    async def delete_by_outfit_id(self, outfit_id: int) -> None:
        stmt = delete(OutfitColor).where(OutfitColor.outfit_id == outfit_id)
        await self._session.execute(stmt)
        await self._session.flush()

