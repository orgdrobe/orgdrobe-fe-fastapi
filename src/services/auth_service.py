from uuid import UUID
from typing import Optional, Any
from datetime import datetime, timedelta, timezone

import jwt
import uuid6
import structlog
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext

from core.enums.auth_roles import AuthRole
from core.configs.jwt_config import jwt_config 
from core.enums.auth_providers import AuthProvider
from core.exceptions.auth_exceptions import (
    UsernameAlreadyExists, EmailAlreadyExists, InvalidCredentials, 
    MissingRefreshToken, InvalidRefreshToken, RefreshTokenRevokedOrExpired,
    RoleNotFound)
from schemas.user import UserRegister, UserRegisterOut, UserLogin, UserLoginOut
from services.interfaces import AuthServiceInterface, UnitOfWorkInterface
from repositories import UserRepository, RoleRepository, UserRoleRepository, UserIdentityRepository, RefreshTokenRepository
from models import User, UserIdentity, UserRole, RefreshToken

logger = structlog.get_logger()

class AuthService(AuthServiceInterface):
    def __init__(self, uow: UnitOfWorkInterface, pwd_context: CryptContext) -> None:
        self._uow = uow 
        self._pwd_context = pwd_context

    async def register_user(self, new_user: UserRegister) -> UserRegisterOut: 
        logger.info("user_registration_attempt", email=new_user.email, username=new_user.username)
        async with self._uow as uow:
            user_repository = uow.get_repo(UserRepository) 
            user_identity_repository = uow.get_repo(UserIdentityRepository) 
            role_repository = uow.get_repo(RoleRepository) 
            user_role_repository = uow.get_repo(UserRoleRepository)

            if await user_repository.get_by_username(new_user.username):
                logger.warning("user_registration_failed", reason="username_taken", username=new_user.username)
                raise UsernameAlreadyExists(new_user.username)

            if await user_repository.get_by_email(new_user.email):
                logger.warning("user_registration_failed", reason="email_taken", email=new_user.email)
                raise EmailAlreadyExists(new_user.email)
        
            user = User(
                username=new_user.username,
                email=new_user.email
            )
            
            await user_repository.add(user)

            hashed_password = self._hash_password(new_user.password)

            user_identity = UserIdentity(
                user_id=user.id,
                provider=AuthProvider.local,
                provider_id=user.email,
                password_hash=hashed_password
            )

            await user_identity_repository.add(user_identity)
            
            role = await role_repository.get_by_name(AuthRole.User)
            if role is None:
                logger.error("default_role_not_found", missing_role=AuthRole.User)
                raise RoleNotFound(AuthRole.User)

            user_role = UserRole(
                user_id=user.id,
                role_id=role.id
            )

            await user_role_repository.add(user_role)
            await uow.commit()
            result = UserRegisterOut.model_validate(user)
            logger.info("user_registered_successfully", user_id=user.id, email=user.email)

        return result
    
    async def local_login(self, user_credentials: UserLogin) -> tuple[UserLoginOut, str]:
        logger.info("user_login_attempt", email=user_credentials.email)
        async with self._uow as uow:
            user_identity_repository = uow.get_repo(UserIdentityRepository) 
            refresh_token_repository = uow.get_repo(RefreshTokenRepository)

            user_identity = await user_identity_repository.get_by_provider_id_with_user_and_roles(user_credentials.email)

            if user_identity is None or not self._verify_password(user_credentials.password, user_identity.password_hash):
                logger.warning("user_login_failed", reason="invalid_credentials", email=user_credentials.email)
                raise InvalidCredentials()
            
            user_roles = []
            for role in user_identity.user.roles:
                user_roles.append(role.name)

            access_payload = {"sub": str(user_identity.user.id), "roles": user_roles}
            access_token = self._create_access_token(access_payload, expires_delta=timedelta(minutes=jwt_config.ACCESS_TOKEN_EXPIRE_MINUTES))

            jti = self._create_refresh_token_jti()
            rt_payload = self._create_refresh_token_payload(jti, expires_delta=timedelta(days=jwt_config.REFRESH_TOKEN_EXPIRE_DAYS))

            rt = RefreshToken(
                jti=jti,
                user_id = user_identity.user.id,
                expires_at = rt_payload["exp"],
                created_at = rt_payload["iat"]
            )
            
            await refresh_token_repository.add(rt)
            refresh_token = jwt.encode(rt_payload.copy(), jwt_config.SECRET_KEY, algorithm=jwt_config.ALGORITHM)
            
            await uow.commit()
            result = UserLoginOut(
                access_token=access_token, 
                token_type="bearer",
                expires_in=jwt_config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

            logger.info("user_logged_in_successfully", user_id=user_identity.user.id, rt_jti=jti)

        return result, refresh_token

    async def refresh_tokens(self, refresh_token: str | None) -> tuple[UserLoginOut, str]:
        if refresh_token is None:
            logger.warning("token_refresh_failed", reason="missing_token")
            raise MissingRefreshToken()     

        payload = self._decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            logger.warning("token_refresh_failed", reason="invalid_or_malformed_token")
            raise InvalidRefreshToken()
        
        jti = payload.get("jti")
        if jti is None:
            logger.warning("token_refresh_failed", reason="missing_jti_in_payload")
            raise InvalidRefreshToken()
        
        async with self._uow as uow:
            refresh_token_repository = uow.get_repo(RefreshTokenRepository)
            
            rt = await refresh_token_repository.get_by_jti_with_user_and_roles(UUID(jti))
            if rt is None or rt.revoked or rt.expires_at < datetime.now(timezone.utc):
                logger.warning("token_refresh_failed", reason="revoked_or_expired", jti=jti)
                raise RefreshTokenRevokedOrExpired()
            
            rt.revoked = True
            
            new_jti = self._create_refresh_token_jti()
            new_rt_payload = self._create_refresh_token_payload(new_jti, expires_delta=timedelta(days=jwt_config.REFRESH_TOKEN_EXPIRE_DAYS))

            new_rt = RefreshToken(
                jti=new_jti,
                user_id = rt.user.id,
                expires_at = new_rt_payload["exp"],
                created_at = new_rt_payload["iat"]
            )
            await refresh_token_repository.add(new_rt)

            new_refresh_token = jwt.encode(new_rt_payload.copy(), jwt_config.SECRET_KEY, algorithm=jwt_config.ALGORITHM)

            user_roles = []
            for role in rt.user.roles:
                user_roles.append(role.name)

            new_access_payload = {"sub": str(rt.user.id), "roles": user_roles}
            new_access_token = self._create_access_token(new_access_payload, expires_delta=timedelta(minutes=jwt_config.ACCESS_TOKEN_EXPIRE_MINUTES))

            await uow.commit()
            result = UserLoginOut(
                access_token=new_access_token, 
                token_type="bearer",
                expires_in=jwt_config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

            logger.info("tokens_refreshed_successfully", old_jti=jti, new_jti=new_jti)

        return result, new_refresh_token

    async def logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            logger.debug("logout_aborted", reason="no_token_provided")
            return

        payload = self._decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            logger.warning("logout_failed", reason="invalid_token_format")
            return

        jti = payload.get("jti")
        async with self._uow as uow:
            repo = uow.get_repo(RefreshTokenRepository)
            rt = await repo.get_by_jti(UUID(jti))
            
            if rt and not rt.revoked:
                rt.revoked = True
                await uow.commit()
                logger.info("user_logged_out", jti=jti)
            else:
                logger.debug("logout_skipped", reason="token_already_revoked_or_not_found", jti=jti)


    def _hash_password(self, password: str) -> str:
        return self._pwd_context.hash(password)
    
    def _verify_password(self, plain: str, hashed: Optional[str]) -> bool:
        return self._pwd_context.verify(plain, hashed)
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        now = datetime.now(timezone.utc)

        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=jwt_config.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "iat": now, 
            "type": "access"
        })
        return jwt.encode(to_encode, jwt_config.SECRET_KEY, algorithm=jwt_config.ALGORITHM)
    
    def _create_refresh_token_jti(self):
        return str(uuid6.uuid7())
    
    def _create_refresh_token_payload(self, jti: str, expires_delta: Optional[timedelta] = None) -> dict:
        now = datetime.now(timezone.utc)
        
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(days=jwt_config.REFRESH_TOKEN_EXPIRE_DAYS)
            
        return {
            "jti": jti, 
            "exp": expire, 
            "iat": now, 
            "type": "refresh"
        }
    
    def _decode_token(self, token: str) -> dict[str,Any] | None:
        try:
            payload = jwt.decode(token, jwt_config.SECRET_KEY, jwt_config.ALGORITHM)
            return payload
        except PyJWTError:
            return None