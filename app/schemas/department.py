import uuid
from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    name: str


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    restaurant_id: uuid.UUID

    model_config = {"from_attributes": True}
