from core.database.database_context import async_session_factory
from services.interfaces import UnitOfWorkInterface
from services.unit_of_work import SqlAlchemyUnitOfWork
from repositories.user_repository import UserRepository
from repositories.identity_repository import UserIdentityRepository
from repositories.user_role_repository import UserRoleRepository
from repositories.role_repository import RoleRepository

def get_unit_of_work() -> UnitOfWorkInterface:
    unit_of_work = SqlAlchemyUnitOfWork(session_factory=async_session_factory)
    
    unit_of_work.register_factory(UserRepository, lambda session: UserRepository(session))
    unit_of_work.register_factory(UserIdentityRepository, lambda session: UserIdentityRepository(session))
    unit_of_work.register_factory(RoleRepository, lambda session: RoleRepository(session))
    unit_of_work.register_factory(UserRoleRepository, lambda session: UserRoleRepository(session))

    return unit_of_work