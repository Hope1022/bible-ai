from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.user import User, UserRole
from models.profile import UserProfile
from models.session import Session
from schemas.user import UserRegisterSchema, UserLoginSchema
from schemas.token import TokenSchema
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
)
from core.exceptions import (
    InvalidCredentialsException,
    EmailAlreadyExistsException,
    InvalidTokenException,
    TokenTypeMismatchException,
)


async def register_user(
    data: UserRegisterSchema,
    db: AsyncSession,
) -> TokenSchema:

    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    existing_user = result.scalars().first()

    if existing_user:
        raise EmailAlreadyExistsException

    password_hash = hash_password(data.password)

    new_user = User(
        email=data.email,
        password_hash=password_hash,
        role=UserRole.member,
    )
    db.add(new_user)

    await db.flush()

    new_profile = UserProfile(
        user_id=new_user.id,
        full_name=data.full_name,
    )
    db.add(new_profile)

    token_data = {"sub": str(new_user.id)}

    access_token  = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    new_session = Session(
        user_id=new_user.id,
        refresh_token=refresh_token,
    )
    db.add(new_session)

    await db.commit()

    return TokenSchema(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def login_user(
    data: UserLoginSchema,
    db: AsyncSession,
) -> TokenSchema:

    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalars().first()

    if not user:
        raise InvalidCredentialsException

    if not verify_password(data.password, user.password_hash):
        raise InvalidCredentialsException

    if not user.is_active:
        raise InvalidCredentialsException

    user.last_login = datetime.now(timezone.utc)

    token_data = {"sub": str(user.id)}

    access_token  = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    new_session = Session(
        user_id=user.id,
        refresh_token=refresh_token,
    )
    db.add(new_session)

    await db.commit()

    return TokenSchema(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession,
) -> TokenSchema:

    payload = decode_token(refresh_token)

    if payload is None:
        raise InvalidTokenException

    if not verify_token_type(payload, "refresh"):
        raise TokenTypeMismatchException

    result = await db.execute(
        select(Session).where(
            Session.refresh_token == refresh_token,
            Session.is_revoked == False,
        )
    )
    session = result.scalars().first()

    if not session:
        raise InvalidTokenException

    token_data = {"sub": payload["sub"]}

    return TokenSchema(
        access_token=create_access_token(token_data),
        refresh_token=refresh_token,
    )


async def logout_user(
    refresh_token: str,
    db: AsyncSession,
) -> None:

    result = await db.execute(
        select(Session).where(
            Session.refresh_token == refresh_token,
        )
    )
    session = result.scalars().first()

    if session:
        session.is_revoked = True
        await db.commit()
