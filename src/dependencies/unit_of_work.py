from core.database.database_context import async_session_factory
from services import SqlAlchemyUnitOfWork
from services.interfaces import UnitOfWorkInterface
from repositories import (UserRepository, UserIdentityRepository, UserRoleRepository, 
                          RoleRepository, RefreshTokenRepository, CategoryMasterRepository,
                          CategorySubRepository, GarmentTypeRepository)
from repositories.interfaces import (UserIdentityRepositoryInterface, UserRepositoryInterface, RoleRepositoryInterface,
                                     UserRoleRepositoryInterface, RefreshTokenRepositoryInterface, CategoryMasterRepositoryInterface,
                                     CategorySubRepositoryInterface, GarmentTypeRepositoryInterface)


def get_unit_of_work() -> UnitOfWorkInterface:
    unit_of_work = SqlAlchemyUnitOfWork(session_factory=async_session_factory)
    
    unit_of_work.register_factory_by_interface(UserRepositoryInterface, lambda session: UserRepository(session))
    unit_of_work.register_factory_by_interface(UserIdentityRepositoryInterface, lambda session: UserIdentityRepository(session))
    unit_of_work.register_factory_by_interface(RoleRepositoryInterface, lambda session: RoleRepository(session))
    unit_of_work.register_factory_by_interface(UserRoleRepositoryInterface, lambda session: UserRoleRepository(session))
    unit_of_work.register_factory_by_interface(RefreshTokenRepositoryInterface, lambda session: RefreshTokenRepository(session))
    unit_of_work.register_factory_by_interface(CategoryMasterRepositoryInterface, lambda session: CategoryMasterRepository(session))
    unit_of_work.register_factory_by_interface(CategorySubRepositoryInterface, lambda session: CategorySubRepository(session))
    unit_of_work.register_factory_by_interface(GarmentTypeRepositoryInterface, lambda session: GarmentTypeRepository(session))

    return unit_of_work