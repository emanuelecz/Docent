from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from datetime import datetime
import uuid
from pgvector.sqlalchemy import Vector
from database.db import Base

class Issue(Base):
    __tablename__  = "github-issues"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    github_number: Mapped[int] = mapped_column(unique=True, index=True)
    title: Mapped[str] 
    original_question: Mapped[str]
    fix_summary:Mapped[str]
    url: Mapped[str]
    closed_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    embeddings:Mapped[list[float]] = mapped_column(Vector(1024))
    
