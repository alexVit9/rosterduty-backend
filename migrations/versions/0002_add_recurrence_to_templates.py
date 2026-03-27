"""Add recurrence fields to checklist_templates

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-25 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("checklist_templates", sa.Column("recurrence_type", sa.String(10), nullable=True))
    op.add_column("checklist_templates", sa.Column("recurrence_day_of_week", sa.SmallInteger(), nullable=True))
    op.add_column("checklist_templates", sa.Column("recurrence_day_of_month", sa.SmallInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("checklist_templates", "recurrence_day_of_month")
    op.drop_column("checklist_templates", "recurrence_day_of_week")
    op.drop_column("checklist_templates", "recurrence_type")
