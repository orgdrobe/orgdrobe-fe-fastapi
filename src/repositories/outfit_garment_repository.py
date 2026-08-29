from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.interfaces import OutfitGarmentRepositoryInterface
from models import OutfitGarment


class OutfitGarmentRepository(OutfitGarmentRepositoryInterface):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, outfit_garment: OutfitGarment) -> OutfitGarment:
        self._session.add(outfit_garment)
        await self._session.flush()
        await self._session.refresh(outfit_garment)
        return outfit_garment

    async def add_range(self, outfit_garment_range: list[OutfitGarment]) -> list[OutfitGarment]:
        self._session.add_all(outfit_garment_range)
        await self._session.flush()
        for og in outfit_garment_range:
            await self._session.refresh(og)
        return outfit_garment_range

    async def delete_by_outfit_id(self, outfit_id: int) -> None:
        stmt = delete(OutfitGarment).where(OutfitGarment.outfit_id == outfit_id)
        await self._session.execute(stmt)
        await self._session.flush()

