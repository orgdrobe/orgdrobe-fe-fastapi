from abc import ABC, abstractmethod

from models import GarmentColor

class GarmentColorRepositoryInterface(ABC):
    @abstractmethod
    async def add(self, garment_color: GarmentColor) -> GarmentColor: ...

    @abstractmethod
    async def add_range(self, garment_color_range: list[GarmentColor]) -> list[GarmentColor]: ...

    @abstractmethod
    async def delete_by_garment_id(self, garment_id: int) -> None: ...