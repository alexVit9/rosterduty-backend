import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    owner: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys=[owner_id], primaryjoin="Restaurant.owner_id == User.id"
    )
    employees: Mapped[list["User"]] = relationship(  # noqa: F821
        "User", back_populates="restaurant", foreign_keys="User.restaurant_id"
    )
    locations: Mapped[list["Location"]] = relationship(
        "Location", back_populates="restaurant", cascade="all, delete-orphan"
    )
    departments: Mapped[list["Department"]] = relationship(  # noqa: F821
        "Department", back_populates="restaurant", cascade="all, delete-orphan"
    )
    checklist_templates: Mapped[list["ChecklistTemplate"]] = relationship(  # noqa: F821
        "ChecklistTemplate", back_populates="restaurant", cascade="all, delete-orphan"
    )


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False
    )

    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="locations")
    checklist_templates: Mapped[list["ChecklistTemplate"]] = relationship(  # noqa: F821
        "ChecklistTemplate", back_populates="location"
    )
