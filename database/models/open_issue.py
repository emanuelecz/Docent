from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, String
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
import uuid
from pgvector.sqlalchemy import Vector
from database.db import Base


class OpenIssue(Base):
    __tablename__ = "open-issues"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    github_number: Mapped[int] = mapped_column(unique=True, index=True)
    title: Mapped[str]
    original_question: Mapped[str]
    body_summary: Mapped[str | None] = mapped_column(nullable=True)
    url: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, server_default="{}")
    embeddings: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)
