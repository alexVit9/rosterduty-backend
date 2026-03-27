import uuid
from datetime import datetime, time, timezone
from sqlalchemy import String, Boolean, DateTime, Time, ForeignKey, Integer, Text, SmallInteger, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ChecklistTemplate(Base):
    __tablename__ = "checklist_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    time_from: Mapped[time | None] = mapped_column(Time, nullable=True)
    time_to: Mapped[time | None] = mapped_column(Time, nullable=True)
    recurrence_type: Mapped[str | None] = mapped_column(String(10), nullable=True)  # 'daily','weekly','monthly'
    recurrence_day_of_week: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)  # 0=Mon..6=Sun
    recurrence_day_of_month: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)  # 1-31
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    location: Mapped["Location"] = relationship(  # noqa: F821
        "Location", back_populates="checklist_templates"
    )
    department: Mapped["Department"] = relationship(  # noqa: F821
        "Department", back_populates="checklist_templates"
    )
    creator: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys=[created_by]
    )
    restaurant: Mapped["Restaurant"] = relationship(  # noqa: F821
        "Restaurant", back_populates="checklist_templates"
    )
    items: Mapped[list["ChecklistItem"]] = relationship(
        "ChecklistItem",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="ChecklistItem.order",
    )
    completed_checklists: Mapped[list["CompletedChecklist"]] = relationship(  # noqa: F821
        "CompletedChecklist", back_populates="template"
    )


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("checklist_templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_photo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    example_photo_urls: Mapped[list | None] = mapped_column(JSON, nullable=True)

    template: Mapped["ChecklistTemplate"] = relationship(
        "ChecklistTemplate", back_populates="items"
    )
