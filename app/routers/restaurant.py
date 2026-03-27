import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import require_manager, get_current_user
from app.services.restaurant_service import (
    get_restaurant_full,
    update_restaurant_name,
    add_location,
    delete_location,
    add_department,
    delete_department,
)
from app.schemas.restaurant import (
    RestaurantResponse,
    RestaurantUpdateRequest,
    LocationCreate,
    LocationResponse,
    DepartmentCreate,
    DepartmentResponse,
)
from app.models.user import User

router = APIRouter(prefix="/restaurant", tags=["restaurant"])


@router.get("/locations/list", response_model=list[LocationResponse])
async def get_locations_for_employee(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.restaurant import Location
    result = await db.execute(
        select(Location).where(Location.restaurant_id == current_user.restaurant_id)
    )
    return [LocationResponse.model_validate(loc) for loc in result.scalars().all()]


@router.get("", response_model=RestaurantResponse)
async def get_restaurant(
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    restaurant = await get_restaurant_full(current_user.restaurant_id, db)
    return RestaurantResponse.model_validate(restaurant)


@router.patch("", response_model=RestaurantResponse)
async def update_restaurant(
    data: RestaurantUpdateRequest,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    await update_restaurant_name(current_user.restaurant_id, data.name, db)
    restaurant = await get_restaurant_full(current_user.restaurant_id, db)
    return RestaurantResponse.model_validate(restaurant)


@router.post("/locations", response_model=LocationResponse, status_code=201)
async def create_location(
    data: LocationCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    location = await add_location(current_user.restaurant_id, data.name, db)
    return LocationResponse.model_validate(location)


@router.delete("/locations/{location_id}", status_code=204)
async def remove_location(
    location_id: uuid.UUID,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    await delete_location(location_id, current_user.restaurant_id, db)


@router.post("/departments", response_model=DepartmentResponse, status_code=201)
async def create_department(
    data: DepartmentCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    department = await add_department(current_user.restaurant_id, data.name, db)
    return DepartmentResponse.model_validate(department)


@router.delete("/departments/{department_id}", status_code=204)
async def remove_department(
    department_id: uuid.UUID,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    await delete_department(department_id, current_user.restaurant_id, db)
