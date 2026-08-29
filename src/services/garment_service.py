import structlog

from core.exceptions.garment_exceptions import GarmentNotFound
from core.exceptions.gender_exceptions import GenderNotFound
from core.exceptions.category_exceptions import MasterCategoryNotFound, SubCategoryNotFound
from core.exceptions.garment_type_exceptions import GarmentTypeNotFound
from core.exceptions.season_exceptions import SeasonNotFound
from core.exceptions.usage_exceptions import UsageNotFound
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
    ColorRepositoryInterface,
    GenderRepositoryInterface,
    CategoryMasterRepositoryInterface,
    CategorySubRepositoryInterface,
    GarmentTypeRepositoryInterface,
    SeasonRepositoryInterface,
    UsageRepositoryInterface
)
from models import Garment, GarmentColor, Color, User

logger = structlog.get_logger()

class GarmentService(GarmentServiceInterface):
    def __init__(self, uow: UnitOfWorkInterface) -> None:
        self._uow = uow 

    async def _validate_foreign_keys(
        self,
        uow: UnitOfWorkInterface,
        gender_id: int | None = None,
        category_master_id: int | None = None,
        category_sub_id: int | None = None,
        garment_type_id: int | None = None,
        season_id: int | None = None,
        usage_id: int | None = None
    ) -> None:
        if gender_id is not None:
            gender_repo = uow.get_repo_by_interface(GenderRepositoryInterface)
            if not await gender_repo.get_by_id(gender_id):
                raise GenderNotFound(gender_id)

        if category_master_id is not None:
            master_repo = uow.get_repo_by_interface(CategoryMasterRepositoryInterface)
            if not await master_repo.get_by_id(category_master_id):
                raise MasterCategoryNotFound(category_master_id)

        if category_sub_id is not None:
            sub_repo = uow.get_repo_by_interface(CategorySubRepositoryInterface)
            if not await sub_repo.get_by_id(category_sub_id):
                raise SubCategoryNotFound(category_sub_id)

        if garment_type_id is not None:
            type_repo = uow.get_repo_by_interface(GarmentTypeRepositoryInterface)
            if not await type_repo.get_by_id(garment_type_id):
                raise GarmentTypeNotFound(garment_type_id)

        if season_id is not None:
            season_repo = uow.get_repo_by_interface(SeasonRepositoryInterface)
            if not await season_repo.get_by_id(season_id):
                raise SeasonNotFound(season_id)

        if usage_id is not None:
            usage_repo = uow.get_repo_by_interface(UsageRepositoryInterface)
            if not await usage_repo.get_by_id(usage_id):
                raise UsageNotFound(usage_id)

    async def create(self, user_id: int, new_garment: NewGarment) -> GarmentOut:
        logger.info("creating_garment", user_id=user_id, name=new_garment.name)
        
        async with self._uow as uow:
            await self._validate_foreign_keys(
                uow=uow,
                gender_id=new_garment.gender_id,
                category_master_id=new_garment.category_master_id,
                category_sub_id=new_garment.category_sub_id,
                garment_type_id=new_garment.garment_type_id,
                season_id=new_garment.season_id,
                usage_id=new_garment.usage_id
            )

            garment_repository = uow.get_repo_by_interface(GarmentRepositoryInterface)
            garment_color_repository = uow.get_repo_by_interface(GarmentColorRepositoryInterface)
            color_repository = uow.get_repo_by_interface(ColorRepositoryInterface)
            
            garment_data = new_garment.model_dump(exclude={"colors"})
            garment = Garment(**garment_data, user_id=user_id)
            garment = await garment_repository.add(garment)

            if new_garment.colors:
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
                logger.error("garment_get_created_failed", reason="not_found", garment_id=garment.id)
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

    async def update(self, user_id: int, id: int, update_data: UpdateGarment) -> GarmentOut:
        logger.info("updating_garment", garment_id=id, user_id=user_id)
        
        async with self._uow as uow:
            garment_repository = uow.get_repo_by_interface(GarmentRepositoryInterface)
            garment_color_repository = uow.get_repo_by_interface(GarmentColorRepositoryInterface)
            color_repository = uow.get_repo_by_interface(ColorRepositoryInterface)
            
            garment = await garment_repository.get_by_id(id)
            if not garment or garment.user_id != user_id:
                logger.warning("garment_update_failed", reason="not_found_or_wrong_ownership", garment_id=id)
                raise GarmentNotFound(id)

            await self._validate_foreign_keys(
                uow=uow,
                gender_id=update_data.gender_id,
                category_master_id=update_data.category_master_id,
                category_sub_id=update_data.category_sub_id,
                garment_type_id=update_data.garment_type_id,
                season_id=update_data.season_id,
                usage_id=update_data.usage_id
            )
                
            data_dict = update_data.model_dump(exclude_unset=True, exclude={"colors"})
            if data_dict:
                await garment_repository.update(garment, data_dict)

            if update_data.colors is not None:
                await garment_color_repository.delete_by_garment_id(garment.id)
                for color_item in update_data.colors:
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
            
            updated_garment = await garment_repository.get_by_id(id)
            if updated_garment is None:
                logger.error("garment_get_updated_failed", reason="not_found", garment_id=id)
                raise GarmentNotFound(id)
            
            result = self._map_garment_to_out(updated_garment)
            logger.info("garment_updated_successfully", garment_id=result.id)
            
        return result

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
