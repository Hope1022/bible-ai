from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.database import get_db
from models.user import User, UserRole
from core.security import decode_token, verify_token_type
from core.exceptions import (
    InvalidTokenException,
    TokenTypeMismatchException,
    InsufficientPermissionsException,
    UserNotFoundException,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(token)

    if payload is None:
        raise InvalidTokenException

    if not verify_token_type(payload, "access"):
        raise TokenTypeMismatchException

    user_id_str = payload.get("sub")

    if user_id_str is None:
        raise InvalidTokenException

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise InvalidTokenException

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()

    if user is None:
        raise UserNotFoundException

    if not user.is_active:
        raise InvalidTokenException

    return user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email address to access this feature.",
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise InsufficientPermissionsException
        return current_user
    return role_checker


__all__ = [
    "get_db",
    "get_current_user",
    "get_current_verified_user",
    "require_role",
    "oauth2_scheme",
]