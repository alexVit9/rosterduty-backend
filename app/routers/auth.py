from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import (
    register_manager,
    login,
    accept_invite,
    get_current_user,
)
from app.schemas.user import (
    ManagerRegisterRequest,
    LoginRequest,
    InviteAcceptRequest,
    TokenResponse,
    UserResponse,
    MeResponse,
)
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/manager", response_model=TokenResponse, status_code=201)
async def register_manager_endpoint(
    data: ManagerRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    user, token = await register_manager(data, db)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user, token = await login(data, db)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.restaurant import Restaurant
    restaurant_name = None
    if current_user.restaurant_id:
        res = await db.execute(select(Restaurant).where(Restaurant.id == current_user.restaurant_id))
        r = res.scalar_one_or_none()
        if r:
            restaurant_name = r.name
    data = MeResponse.model_validate(current_user)
    data.restaurant_name = restaurant_name
    return data


@router.post("/invite/accept", response_model=TokenResponse)
async def accept_invite_endpoint(
    data: InviteAcceptRequest,
    db: AsyncSession = Depends(get_db),
):
    user, token = await accept_invite(data, db)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
