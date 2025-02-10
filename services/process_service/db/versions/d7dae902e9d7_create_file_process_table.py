"""create_file_process_table

Revision ID: d7dae902e9d7
Revises:
Create Date: 2025-01-30 20:59:28.810465

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d7dae902e9d7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "file_process",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("total_frames", sa.Integer, nullable=False),
        sa.Column("file_size", sa.Integer, nullable=False),
        sa.Column("s3_path", sa.String, nullable=False),
        sa.Column("uploaded_at", sa.DateTime, nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("file_process")
