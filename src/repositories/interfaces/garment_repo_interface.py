from typing import Any, Sequence
from abc import ABC, abstractmethod

from models import Garment

class GarmentRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Garment | None: ...
    
    @abstractmethod 
    async def add(self, user: Garment) -> Garment: ...

    @abstractmethod
    async def get_all_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> Sequence[Garment]: ...

    # @abstractmethod
    # async def update(self, garment: Garment, update_data: dict[str, Any]) -> Garment | None: ...

    @abstractmethod
    async def delete(self, id: int) -> bool: ...
