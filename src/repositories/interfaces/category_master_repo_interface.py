from typing import Any
from abc import ABC, abstractmethod

from models import CategoryMaster

class CategoryMasterRepositoryInterface(ABC):
    @abstractmethod
    async def add(self, category_master: CategoryMaster) -> CategoryMaster: ...

    @abstractmethod
    async def get_by_id(self, id: int) -> CategoryMaster | None: ...

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[CategoryMaster]: ...

    @abstractmethod
    async def update(self, category_master: CategoryMaster, new_category_data: dict[str, Any]) -> CategoryMaster | None: ...

    @abstractmethod
    async def delete(self, category_id: int) -> bool: ...