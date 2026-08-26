from fastapi import Depends

from services import CategoryMasterService
from services.interfaces import UnitOfWorkInterface, CategoryMasterServiceInterface
from .unit_of_work import get_unit_of_work

def get_category_master_service(uow: UnitOfWorkInterface = Depends(get_unit_of_work)) -> CategoryMasterServiceInterface: 
    return CategoryMasterService(uow)