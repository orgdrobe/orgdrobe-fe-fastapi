from abc import ABC, abstractmethod

from models import OutfitColor


class OutfitColorRepositoryInterface(ABC):
    @abstractmethod
    async def add(self, outfit_color: OutfitColor) -> OutfitColor: ...

    @abstractmethod
    async def add_range(self, outfit_color_range: list[OutfitColor]) -> list[OutfitColor]: ...

    @abstractmethod
    async def delete_by_outfit_id(self, outfit_id: int) -> None: ...

