import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from app.models.user import AccessLevel


class UserBase(BaseModel):
    name: str
    email: EmailStr
    position: Optional[str] = None


class ManagerRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    restaurant_name: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class InviteAcceptRequest(BaseModel):
    invite_token: str
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class InviteUserRequest(BaseModel):
    name: str
    email: EmailStr
    position: Optional[str] = None


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    position: Optional[str] = None
    access_level: AccessLevel
    restaurant_id: Optional[uuid.UUID] = None
    invite_accepted: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MeResponse(UserResponse):
    restaurant_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
