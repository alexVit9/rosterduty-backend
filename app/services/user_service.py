import uuid
import random
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, AccessLevel
from app.core.email import send_invite_email
from app.schemas.user import InviteUserRequest, UpdateUserRequest


async def get_restaurant_employees(restaurant_id: uuid.UUID, db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User).where(
            User.restaurant_id == restaurant_id,
            User.access_level == AccessLevel.employee,
        )
    )
    return list(result.scalars().all())


async def invite_employee(
    data: InviteUserRequest,
    restaurant_id: uuid.UUID,
    restaurant_name: str,
    db: AsyncSession,
) -> User:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    invite_token = f"{random.randint(0, 9999):04d}"

    employee = User(
        id=uuid.uuid4(),
        name=data.name,
        email=data.email,
        position=data.position,
        access_level=AccessLevel.employee,
        restaurant_id=restaurant_id,
        invite_token=invite_token,
        invite_accepted=False,
    )
    db.add(employee)
    await db.commit()
    await db.refresh(employee)

    await send_invite_email(
        recipient_email=data.email,
        recipient_name=data.name,
        restaurant_name=restaurant_name,
        invite_token=invite_token,
    )

    return employee


async def update_employee(
    employee_id: uuid.UUID,
    data: UpdateUserRequest,
    restaurant_id: uuid.UUID,
    db: AsyncSession,
) -> User:
    result = await db.execute(
        select(User).where(
            User.id == employee_id,
            User.restaurant_id == restaurant_id,
        )
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    if data.name is not None:
        employee.name = data.name
    if data.position is not None:
        employee.position = data.position

    await db.commit()
    await db.refresh(employee)
    return employee


async def delete_employee(
    employee_id: uuid.UUID,
    restaurant_id: uuid.UUID,
    db: AsyncSession,
) -> None:
    result = await db.execute(
        select(User).where(
            User.id == employee_id,
            User.restaurant_id == restaurant_id,
            User.access_level == AccessLevel.employee,
        )
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    await db.delete(employee)
    await db.commit()
