"""split issues into closed-issues and open-issues

Renames the existing corpus table github-issues -> closed-issues (data preserved
in place, identical columns) and creates the new, empty open-issues queue table.

Revision ID: b7e2c1a9f4d3
Revises: 32d36e234bec
Create Date: 2026-08-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "b7e2c1a9f4d3"
down_revision: Union[str, Sequence[str], None] = "32d36e234bec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Preserve the corpus: rename the existing table in place, no data touched.
    op.rename_table("github-issues", "closed-issues")

    # New, empty queue table for open issues (body_summary + embeddings filled
    # lazily at intake, hence nullable).
    op.create_table(
        "open-issues",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("github_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("original_question", sa.String(), nullable=False),
        sa.Column("body_summary", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("tags", ARRAY(sa.String()), server_default="{}", nullable=False),
        sa.Column("embeddings", Vector(1024), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_open-issues_github_number", "open-issues", ["github_number"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_open-issues_github_number", table_name="open-issues")
    op.drop_table("open-issues")
    op.rename_table("closed-issues", "github-issues")
