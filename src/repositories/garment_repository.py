from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.interfaces import GarmentRepositoryInterface
from models import Garment, GarmentColor


def _garment_eager_options():
    return [
        selectinload(Garment.gender),
        selectinload(Garment.category_master),
        selectinload(Garment.category_sub),
        selectinload(Garment.garment_type),
        selectinload(Garment.season),
        selectinload(Garment.usage),
        selectinload(Garment.garment_colors).joinedload(GarmentColor.color),
    ]


class GarmentRepository(GarmentRepositoryInterface):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, garment: Garment) -> Garment: 
        self._session.add(garment)
        await self._session.flush()
        await self._session.refresh(garment)
        return garment

    async def get_by_id(self, id: int) -> Garment | None:
        stmt = (
            select(Garment)
            .where(Garment.id == id)
            .options(*_garment_eager_options())
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Garment]: 
        stmt = (
            select(Garment)
            .where(Garment.user_id == user_id)
            .options(*_garment_eager_options())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
        
    # async def update(self, garment: Garment, update_data: dict[str, Any]) -> Garment | None:
    #     stmt = (
    #         update(Garment)
    #         .where(Garment.id == garment.id)
    #         .values(**update_data)
    #     )
    #     await self._session.execute(stmt)
    #     await self._session.flush()
        
    #     return await self.get_by_id(garment.id)
        
    async def delete(self, id: int) -> bool:
        stmt = select(Garment).where(Garment.id == id)
        result = await self._session.execute(stmt)
        garment = result.scalar_one_or_none()
        if not garment:
            return False
                    
        await self._session.delete(garment)
        await self._session.flush()
        return True