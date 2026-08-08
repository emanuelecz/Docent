from pydantic import BaseModel
from datetime import datetime


class FetchedIssue(BaseModel):
    github_number: int
    title: str
    original_question: str
    fix_summary: str = ""
    url: str
    closed_at: datetime | None = None
    tags: list[str] = []


class IssueCreate(FetchedIssue):
    embeddings: list[float]
