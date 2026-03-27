import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.restaurant import Restaurant, Location
from app.models.department import Department
from app.models.user import User


async def get_restaurant_full(restaurant_id: uuid.UUID, db: AsyncSession) -> Restaurant:
    result = await db.execute(
        select(Restaurant)
        .options(
            selectinload(Restaurant.locations),
            selectinload(Restaurant.departments),
            selectinload(Restaurant.employees),
        )
        .where(Restaurant.id == restaurant_id)
    )
    restaurant = result.scalar_one_or_none()

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return restaurant


async def update_restaurant_name(
    restaurant_id: uuid.UUID, name: str, db: AsyncSession
) -> Restaurant:
    result = await db.execute(
        select(Restaurant).where(Restaurant.id == restaurant_id)
    )
    restaurant = result.scalar_one_or_none()

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    restaurant.name = name
    await db.commit()
    await db.refresh(restaurant)
    return restaurant


async def add_location(
    restaurant_id: uuid.UUID, name: str, db: AsyncSession
) -> Location:
    location = Location(
        id=uuid.uuid4(),
        name=name,
        restaurant_id=restaurant_id,
    )
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location


async def delete_location(
    location_id: uuid.UUID, restaurant_id: uuid.UUID, db: AsyncSession
) -> None:
    result = await db.execute(
        select(Location).where(
            Location.id == location_id,
            Location.restaurant_id == restaurant_id,
        )
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    await db.delete(location)
    await db.commit()


async def add_department(
    restaurant_id: uuid.UUID, name: str, db: AsyncSession
) -> Department:
    department = Department(
        id=uuid.uuid4(),
        name=name,
        restaurant_id=restaurant_id,
    )
    db.add(department)
    await db.commit()
    await db.refresh(department)
    return department


async def delete_department(
    department_id: uuid.UUID, restaurant_id: uuid.UUID, db: AsyncSession
) -> None:
    result = await db.execute(
        select(Department).where(
            Department.id == department_id,
            Department.restaurant_id == restaurant_id,
        )
    )
    department = result.scalar_one_or_none()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    await db.delete(department)
    await db.commit()
