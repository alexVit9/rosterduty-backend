import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.user import UserResponse


class LocationCreate(BaseModel):
    name: str


class LocationResponse(BaseModel):
    id: uuid.UUID
    name: str
    restaurant_id: uuid.UUID

    model_config = {"from_attributes": True}


class DepartmentCreate(BaseModel):
    name: str


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    restaurant_id: uuid.UUID

    model_config = {"from_attributes": True}


class RestaurantUpdateRequest(BaseModel):
    name: str


class RestaurantResponse(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    created_at: datetime
    locations: List[LocationResponse] = []
    departments: List[DepartmentResponse] = []
    employees: List[UserResponse] = []

    model_config = {"from_attributes": True}


class RestaurantBasicResponse(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
