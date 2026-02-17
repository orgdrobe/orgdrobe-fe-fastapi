
from passlib.context import CryptContext

from core.exceptions.auth_exceptions import UsernameAlreadyExists, EmailAlreadyExists
from core.enums.auth_providers import AuthProvider
from core.enums.roles import Role
from schemas.user import UserRegister, UserOut
from services.unit_of_work import UnitOfWorkInterface
from services.interfaces import AuthServiceInterface
from repositories import UserRepository, RoleRepository, UserRoleRepository, UserIdentityRepository
from models import User, UserIdentity, UserRole

class AuthService(AuthServiceInterface):
    def __init__(self, uow: UnitOfWorkInterface, pwd_context: CryptContext) -> None:
        self._uow = uow 
        self._pwd_context = pwd_context

    async def register_user(self, new_user: UserRegister) -> UserOut: 
        async with self._uow:
            user_repository = self._uow.get_repo(UserRepository) 
            user_identity_repository = self._uow.get_repo(UserIdentityRepository) 
            role_repository = self._uow.get_repo(RoleRepository) 
            user_role_repository = self._uow.get_repo(UserRoleRepository)

            if await user_repository.get_user_by_username(new_user.username):
                raise UsernameAlreadyExists(new_user.username)

            if await user_repository.get_user_by_email(new_user.email):
                raise EmailAlreadyExists(new_user.email) # TODO: check message output for security
        
            user = User(
                username=new_user.username,
                email=new_user.email
            )
            
            await user_repository.add_user(user)

            hashed_password = self._hash_password(new_user.password)

            user_identity = UserIdentity(
                user_id=user.id,
                provider=AuthProvider.local,
                provider_id=user.email,
                password_hash=hashed_password
            )

            await user_identity_repository.add_user_identity(user_identity)
            
            role = await role_repository.get_role_by_name(Role.User)
            if role is None:
                raise Exception() # TODO: change to RoleNotFound

            user_role = UserRole(
                user_id=user.id,
                role_id=role.id
            )

            await user_role_repository.add_user_role(user_role)
            await self._uow.commit()
            result = UserOut.model_validate(user)
            
        return result
    
    def _hash_password(self, password: str) -> str:
        return self._pwd_context.hash(password)
    
    def _verify_password(self, plain: str, hashed: str) -> bool:
        return self._pwd_context.verify(plain, hashed)