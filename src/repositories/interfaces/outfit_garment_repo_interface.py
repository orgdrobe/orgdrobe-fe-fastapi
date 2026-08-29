from abc import ABC, abstractmethod

from models import OutfitGarment


class OutfitGarmentRepositoryInterface(ABC):
    @abstractmethod
    async def add(self, outfit_garment: OutfitGarment) -> OutfitGarment: ...

    @abstractmethod
    async def add_range(self, outfit_garment_range: list[OutfitGarment]) -> list[OutfitGarment]: ...

    @abstractmethod
    async def delete_by_outfit_id(self, outfit_id: int) -> None: ...

