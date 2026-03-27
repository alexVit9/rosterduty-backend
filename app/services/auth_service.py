import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.models.user import User, AccessLevel
from app.models.restaurant import Restaurant
from app.schemas.user import ManagerRegisterRequest, LoginRequest, InviteAcceptRequest

bearer_scheme = HTTPBearer()


async def register_manager(
    data: ManagerRegisterRequest, db: AsyncSession
) -> tuple[User, str]:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    manager = User(
        id=uuid.uuid4(),
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        access_level=AccessLevel.manager,
        invite_accepted=True,
    )
    db.add(manager)
    await db.flush()

    restaurant = Restaurant(
        id=uuid.uuid4(),
        name=data.restaurant_name,
        owner_id=manager.id,
    )
    db.add(restaurant)
    await db.flush()

    manager.restaurant_id = restaurant.id
    await db.commit()
    await db.refresh(manager)

    token = create_access_token({"sub": str(manager.id), "role": manager.access_level.value})
    return manager, token


async def login(data: LoginRequest, db: AsyncSession) -> tuple[User, str]:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.invite_accepted and user.access_level == AccessLevel.employee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please complete your registration using the invite link",
        )

    token = create_access_token({"sub": str(user.id), "role": user.access_level.value})
    return user, token


async def accept_invite(data: InviteAcceptRequest, db: AsyncSession) -> tuple[User, str]:
    result = await db.execute(
        select(User).where(User.invite_token == data.invite_token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invite token",
        )

    if user.invite_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite already accepted",
        )

    # Check token expiry (7 days from creation)
    if user.created_at < datetime.now(timezone.utc) - timedelta(days=7):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite token has expired",
        )

    user.password_hash = hash_password(data.password)
    user.invite_accepted = True
    user.invite_token = None
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.access_level.value})
    return user, token


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def require_manager(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.access_level != AccessLevel.manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required",
        )
    return current_user
