import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class CompletedChecklist(Base):
    __tablename__ = "completed_checklists"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("checklist_templates.id", ondelete="RESTRICT"),
        nullable=False,
    )
    template_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    completed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    template: Mapped["ChecklistTemplate"] = relationship(  # noqa: F821
        "ChecklistTemplate", back_populates="completed_checklists"
    )
    completed_by_user: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="completed_checklists", foreign_keys=[completed_by]
    )
    items: Mapped[list["CompletedChecklistItem"]] = relationship(
        "CompletedChecklistItem",
        back_populates="completed_checklist",
        cascade="all, delete-orphan",
    )


class CompletedChecklistItem(Base):
    __tablename__ = "completed_checklist_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    completed_checklist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("completed_checklists.id", ondelete="CASCADE"),
        nullable=False,
    )
    checklist_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("checklist_items.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    requires_photo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    completed_checklist: Mapped["CompletedChecklist"] = relationship(
        "CompletedChecklist", back_populates="items"
    )
    checklist_item: Mapped["ChecklistItem"] = relationship(  # noqa: F821
        "ChecklistItem"
    )
