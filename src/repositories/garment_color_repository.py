
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.interfaces import GarmentColorRepositoryInterface
from models import GarmentColor

class GarmentColorRepository(GarmentColorRepositoryInterface): 
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, garment_color: GarmentColor) -> GarmentColor:
        self._session.add(garment_color)
        await self._session.flush()
        await self._session.refresh(garment_color)
        return garment_color

    async def add_range(self, garment_color_range: list[GarmentColor]) -> list[GarmentColor]: 
        self._session.add_all(garment_color_range)
        await self._session.flush()
        for garment_color in garment_color_range:
            await self._session.refresh(garment_color)
        return garment_color_range

    async def delete_by_garment_id(self, garment_id: int) -> None:
        stmt = delete(GarmentColor).where(GarmentColor.garment_id == garment_id)
        await self._session.execute(stmt)
        await self._session.flush()
