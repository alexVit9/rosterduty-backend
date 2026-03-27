"""Change example_photo_url to example_photo_urls (JSON array)

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-25 00:00:00.000000
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("checklist_items", sa.Column("example_photo_urls", sa.JSON(), nullable=True))
    # Migrate existing data: wrap single URL into array
    op.execute("""
        UPDATE checklist_items
        SET example_photo_urls = json_build_array(example_photo_url)
        WHERE example_photo_url IS NOT NULL
    """)
    op.drop_column("checklist_items", "example_photo_url")


def downgrade() -> None:
    op.add_column("checklist_items", sa.Column("example_photo_url", sa.String(1024), nullable=True))
    op.drop_column("checklist_items", "example_photo_urls")
