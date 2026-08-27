from sqlalchemy.ext.asyncio import AsyncSession

from repositories.interfaces import ColorRepositoryInterface
from repositories.generic_repository import GenericRepository
from models import Color


class ColorRepository(GenericRepository[Color], ColorRepositoryInterface):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Color)

