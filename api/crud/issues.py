from sqlalchemy.orm import Session
from database.models.issue import Issue
from schemas.issues_schemas import IssueCreate


def create_issue(db:Session,issue: IssueCreate):
    db_issue = Issue(
        github_number = issue.github_number,
        title=issue.title,
        original_question=issue.original_question,
        fix_summary=issue.fix_summary,
        url=issue.url,
        closed_at= issue.closed_at,
        tags=issue.tags,
        embeddings=issue.embeddings
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

