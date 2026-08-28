import structlog

from core.exceptions.garment_exceptions import GarmentNotFound
from core.exceptions.auth_exceptions import InsufficientRole
from schemas.garment import NewGarment, UpdateGarment, GarmentOut, GarmentColorOut
from schemas.gender import GenderOut
from schemas.master_category import MasterCategoryOut
from schemas.sub_category import SubCategoryOut
from schemas.garment_type import GarmentTypeOut
from schemas.season import SeasonOut
from schemas.usage import UsageOut
from services.interfaces import UnitOfWorkInterface, GarmentServiceInterface
from repositories.interfaces import (
    GarmentRepositoryInterface,
    GarmentColorRepositoryInterface,
    ColorRepositoryInterface
)
from models import Garment, GarmentColor, Color, User

logger = structlog.get_logger()

class GarmentService(GarmentServiceInterface):
    def __init__(self, uow: UnitOfWorkInterface) -> None:
        self._uow = uow 

    async def create(self, user_id: int, new_garment: NewGarment) -> GarmentOut:
        logger.info("creating_garment", user_id=user_id, name=new_garment.name)
        
        async with self._uow as uow:
            garment_repository = uow.get_repo_by_interface(GarmentRepositoryInterface)
            garment_color_repository = uow.get_repo_by_interface(GarmentColorRepositoryInterface)
            color_repository = uow.get_repo_by_interface(ColorRepositoryInterface)
            
            garment_data = new_garment.model_dump(exclude={"colors"})
            garment = Garment(**garment_data, user_id=user_id)
            garment = await garment_repository.add(garment)

            for color_item in new_garment.colors:
                color = await color_repository.get_by_rgb(color_item.red, color_item.green, color_item.blue)
                if not color:
                    color = Color(red=color_item.red, green=color_item.green, blue=color_item.blue)
                    color = await color_repository.add(color)

                garment_color = GarmentColor(
                    garment_id=garment.id,
                    color_id=color.id,
                    is_primary=color_item.is_primary
                )
                await garment_color_repository.add(garment_color)

            await uow.commit()
            
            created_garment = await garment_repository.get_by_id(garment.id)
            if created_garment is None:
                logger.error("garment_get_created_failed", reason="not_found", garment_id=id)
                raise GarmentNotFound(garment.id)
            
            result = self._map_garment_to_out(created_garment)
            logger.info("garment_created_successfully", garment_id=result.id)
            
        return result

    async def get_by_id(self, user_id: int, id: int) -> GarmentOut:
        async with self._uow as uow:
            garment_repository = uow.get_repo_by_interface(GarmentRepositoryInterface)
            
            garment = await garment_repository.get_by_id(id)
            if garment is None or garment.user_id != user_id:
                logger.warning("garment_get_failed", reason="not_found_or_wrong_ownership", garment_id=id)
                raise GarmentNotFound(id)

            result = self._map_garment_to_out(garment)
            
        return result

    async def get_all_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> list[GarmentOut]:
        async with self._uow as uow:
            garment_repository = uow.get_repo_by_interface(GarmentRepositoryInterface)
            
            garments = await garment_repository.get_all_by_user_id(user_id=user_id, skip=skip, limit=limit)
            result = [self._map_garment_to_out(g) for g in garments]
            
        return result

    # async def update(self, user_id: int, id: int, update_data: UpdateGarment) -> GarmentOut:
    #     logger.info("updating_garment", garment_id=id, user_id=user_id)
        
    #     async with self._uow as uow:
    #         garment_repository = uow.get_repo_by_interface(GarmentRepositoryInterface)
            
    #         garment = await garment_repository.get_by_id(id)
    #         if not garment or garment.user_id != user_id:
    #             logger.warning("garment_update_failed", reason="not_found_or_wrong_ownership", garment_id=id)
    #             raise GarmentNotFound(id)
                
    #         data_dict = update_data.model_dump(exclude_unset=True)
            
    #         await garment_repository.update(garment, data_dict)
    #         await uow.commit()
            
    #         updated_garment = await garment_repository.get_by_id(id)
    #         if updated_garment is None:
    #             logger.error("garment_get_updated_failed", reason="not_found", garment_id=id)
    #             raise GarmentNotFound(id)
            
    #         result = self._map_garment_to_out(updated_garment)
    #         logger.info("garment_updated_successfully", garment_id=result.id)
            
    #     return result

    async def delete(self, user_id: int, id: int) -> bool:
        logger.info("deleting_garment", garment_id=id, user_id=user_id)
        
        async with self._uow as uow:
            garment_repository = uow.get_repo_by_interface(GarmentRepositoryInterface)
            
            garment = await garment_repository.get_by_id(id)
            if not garment or garment.user_id != user_id:
                logger.warning("garment_delete_failed", reason="not_found", garment_id=id)
                raise GarmentNotFound(id)
                
            is_deleted = await garment_repository.delete(id)
            if not is_deleted:
                raise GarmentNotFound(id)
                
            await uow.commit()
            logger.info("garment_deleted_successfully", garment_id=id)
            
        return True

    def _map_garment_to_out(self, garment: Garment) -> GarmentOut:
        colors_out = [
            GarmentColorOut(
                id=gc.color.id,
                red=gc.color.red,
                green=gc.color.green,
                blue=gc.color.blue,
                is_primary=gc.is_primary,
            )
            for gc in (garment.garment_colors or [])
        ]
        return GarmentOut(
            id=garment.id,
            name=garment.name,
            description=garment.description,
            user_id=garment.user_id,
            gender=GenderOut.model_validate(garment.gender),
            category_master=MasterCategoryOut.model_validate(garment.category_master),
            category_sub=SubCategoryOut.model_validate(garment.category_sub),
            garment_type=GarmentTypeOut.model_validate(garment.garment_type),
            season=SeasonOut.model_validate(garment.season),
            usage=UsageOut.model_validate(garment.usage),
            colors=colors_out,
        )
