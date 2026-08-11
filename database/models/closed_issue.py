from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, String, Computed
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from datetime import datetime
import uuid
from pgvector.sqlalchemy import Vector
from database.db import Base

class ClosedIssue(Base):
    __tablename__  = "closed-issues"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    github_number: Mapped[int] = mapped_column(unique=True, index=True)
    title: Mapped[str]
    original_question: Mapped[str]
    fix_summary:Mapped[str]
    url: Mapped[str]
    closed_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, server_default="{}")
    embeddings:Mapped[list[float]] = mapped_column(Vector(1024))
    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('english', coalesce(title, '') || ' ' || coalesce(original_question, ''))",
            persisted=True,
        ),
        nullable=True,
    )
