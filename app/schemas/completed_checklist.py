import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


class CompletedItemSubmit(BaseModel):
    checklist_item_id: uuid.UUID
    completed: bool
    photo_url: Optional[str] = None
    comment: Optional[str] = None


class CompleteChecklistRequest(BaseModel):
    template_id: uuid.UUID
    items: List[CompletedItemSubmit]
    client_date: Optional[date] = None  # local date from client, used instead of UTC server date


class CompletedChecklistItemResponse(BaseModel):
    id: uuid.UUID
    checklist_item_id: uuid.UUID
    name: str
    requires_photo: bool
    completed: bool
    photo_url: Optional[str] = None
    comment: Optional[str] = None

    model_config = {"from_attributes": True}


class CompletedChecklistResponse(BaseModel):
    id: uuid.UUID
    template_id: uuid.UUID
    template_name: str
    date: date
    completed_by: uuid.UUID
    completed_by_name: Optional[str] = None
    restaurant_id: uuid.UUID
    location_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    created_at: datetime
    total_items: int = 0
    completed_items: int = 0
    items: List[CompletedChecklistItemResponse] = []

    model_config = {"from_attributes": True}


class CompletedChecklistSummary(BaseModel):
    id: uuid.UUID
    template_id: uuid.UUID
    template_name: str
    date: date
    completed_by: uuid.UUID
    completed_by_name: Optional[str] = None
    restaurant_id: uuid.UUID
    location_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    created_at: datetime
    total_items: int = 0
    completed_items: int = 0

    model_config = {"from_attributes": True}


class DashboardTemplateEntry(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    location_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    department_name: Optional[str] = None
    time_from: Optional[str] = None
    time_to: Optional[str] = None
    recurrence_type: Optional[str] = None
    recurrence_day_of_week: Optional[int] = None
    recurrence_day_of_month: Optional[int] = None
    is_completed: bool
    completed_by_name: Optional[str] = None
    total_items: int = 0
    completed_items: int = 0


class DashboardLocationGroup(BaseModel):
    location_name: str
    templates: List[DashboardTemplateEntry]


class SubscriptionRequestBody(BaseModel):
    plan: str  # "professional" | "corporate"
    billing: str  # "monthly" | "yearly"
