import uuid
from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel


class ChecklistItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    requires_photo: bool = False
    order: int = 0
    example_photo_urls: Optional[List[str]] = None


class ChecklistItemUpdate(BaseModel):
    id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    requires_photo: bool = False
    order: int = 0
    example_photo_urls: Optional[List[str]] = None


class ChecklistItemResponse(BaseModel):
    id: uuid.UUID
    template_id: uuid.UUID
    name: str
    description: Optional[str] = None
    requires_photo: bool
    order: int
    example_photo_urls: Optional[List[str]] = None

    model_config = {"from_attributes": True}


class ChecklistTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    time_from: Optional[time] = None
    time_to: Optional[time] = None
    recurrence_type: Optional[str] = None          # 'daily', 'weekly', 'monthly'
    recurrence_day_of_week: Optional[int] = None   # 0=Mon..6=Sun
    recurrence_day_of_month: Optional[int] = None  # 1-31
    items: List[ChecklistItemCreate] = []


class ChecklistTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    time_from: Optional[time] = None
    time_to: Optional[time] = None
    recurrence_type: Optional[str] = None
    recurrence_day_of_week: Optional[int] = None
    recurrence_day_of_month: Optional[int] = None
    items: Optional[List[ChecklistItemUpdate]] = None


class ChecklistTemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    location_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    time_from: Optional[time] = None
    time_to: Optional[time] = None
    recurrence_type: Optional[str] = None
    recurrence_day_of_week: Optional[int] = None
    recurrence_day_of_month: Optional[int] = None
    created_by: uuid.UUID
    restaurant_id: uuid.UUID
    created_at: datetime
    items: List[ChecklistItemResponse] = []

    model_config = {"from_attributes": True}


class ActiveTemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    location_id: Optional[uuid.UUID] = None
    location_name: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    department_name: Optional[str] = None
    time_from: Optional[time] = None
    time_to: Optional[time] = None
    recurrence_type: Optional[str] = None
    recurrence_day_of_week: Optional[int] = None
    recurrence_day_of_month: Optional[int] = None
    restaurant_id: uuid.UUID
    items: List[ChecklistItemResponse] = []
    is_completed: bool

    model_config = {"from_attributes": True}
