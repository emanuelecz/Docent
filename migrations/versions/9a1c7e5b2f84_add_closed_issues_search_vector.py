"""add search_vector fts column to closed-issues

Adds a generated tsvector column over title + original_question and a GIN index so
keyword_retrieval's full-text search works.

Revision ID: 9a1c7e5b2f84
Revises: b7e2c1a9f4d3
Create Date: 2026-08-11

"""
from typing import Sequence, Union

from alembic import op


revision: str = "9a1c7e5b2f84"
down_revision: Union[str, Sequence[str], None] = "b7e2c1a9f4d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        'ALTER TABLE "closed-issues" '
        "ADD COLUMN search_vector tsvector GENERATED ALWAYS AS "
        "(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(original_question, ''))) STORED"
    )
    op.execute(
        'CREATE INDEX "ix_closed-issues_search_vector" '
        'ON "closed-issues" USING GIN (search_vector)'
    )


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS "ix_closed-issues_search_vector"')
    op.execute('ALTER TABLE "closed-issues" DROP COLUMN IF EXISTS search_vector')
