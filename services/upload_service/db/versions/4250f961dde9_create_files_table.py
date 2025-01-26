"""create_files_table

Revision ID: 4250f961dde9
Revises:
Create Date: 2025-01-26 17:38:15.769269

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4250f961dde9"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "files",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("s3_path", sa.String(500), nullable=False),
        sa.Column("uploaded_at", sa.DateTime, nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("files")
