import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import require_manager
from app.services.user_service import (
    get_restaurant_employees,
    invite_employee,
    update_employee,
    delete_employee,
)
from app.schemas.user import InviteUserRequest, UpdateUserRequest, UserResponse
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def list_employees(
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    employees = await get_restaurant_employees(current_user.restaurant_id, db)
    return [UserResponse.model_validate(e) for e in employees]


@router.post("/invite", response_model=UserResponse, status_code=201)
async def invite_employee_endpoint(
    data: InviteUserRequest,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.restaurant import Restaurant

    result = await db.execute(
        select(Restaurant).where(Restaurant.id == current_user.restaurant_id)
    )
    restaurant = result.scalar_one_or_none()
    restaurant_name = restaurant.name if restaurant else "the restaurant"

    employee = await invite_employee(
        data,
        current_user.restaurant_id,
        restaurant_name,
        db,
    )
    return UserResponse.model_validate(employee)


@router.patch("/{employee_id}", response_model=UserResponse)
async def update_employee_endpoint(
    employee_id: uuid.UUID,
    data: UpdateUserRequest,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    employee = await update_employee(
        employee_id, data, current_user.restaurant_id, db
    )
    return UserResponse.model_validate(employee)


@router.post("/{employee_id}/resend-invite", status_code=200)
async def resend_invite_endpoint(
    employee_id: uuid.UUID,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.user import User as UserModel, AccessLevel
    from app.models.restaurant import Restaurant
    from app.core.email import send_invite_email

    result = await db.execute(
        select(UserModel).where(
            UserModel.id == employee_id,
            UserModel.restaurant_id == current_user.restaurant_id,
            UserModel.access_level == AccessLevel.employee,
        )
    )
    employee = result.scalar_one_or_none()
    if not employee:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Employee not found")

    if employee.invite_accepted:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail="Employee already registered")

    rest_result = await db.execute(
        select(Restaurant).where(Restaurant.id == current_user.restaurant_id)
    )
    restaurant = rest_result.scalar_one_or_none()
    restaurant_name = restaurant.name if restaurant else "the restaurant"

    await send_invite_email(
        recipient_email=employee.email,
        recipient_name=employee.name,
        restaurant_name=restaurant_name,
        invite_token=employee.invite_token,
    )
    return {"detail": "Invite resent successfully"}


@router.delete("/{employee_id}", status_code=204)
async def delete_employee_endpoint(
    employee_id: uuid.UUID,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    await delete_employee(employee_id, current_user.restaurant_id, db)
