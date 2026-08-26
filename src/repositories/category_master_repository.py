from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.interfaces import CategoryMasterRepositoryInterface
from models import CategoryMaster

class CategoryMasterRepository(CategoryMasterRepositoryInterface):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, category_master: CategoryMaster) -> CategoryMaster: 
        self._session.add(category_master)
        await self._session.flush()
        await self._session.refresh(category_master)
        return category_master            
    
    async def get_by_id(self, id: int) -> CategoryMaster | None:
        stmt = select(CategoryMaster).where(CategoryMaster.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[CategoryMaster]: 
        stmt = select(CategoryMaster).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, category_master: CategoryMaster, new_category_data: dict[str, Any]) -> CategoryMaster | None:
        for key, value in new_category_data.items():
            setattr(category_master, key, value)
            
        self._session.add(category_master) 
        await self._session.flush()
        await self._session.refresh(category_master)
        return category_master
    
    async def delete(self, category_id: int) -> bool:
        category_master = await self.get_by_id(category_id)
        
        if not category_master:
            return False
            
        await self._session.delete(category_master)
        await self._session.flush()
        return True