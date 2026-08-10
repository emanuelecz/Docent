from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models.closed_issue import ClosedIssue
from database.models.open_issue import OpenIssue
from ingestion.issues import fetch_closed_issues_by_number
from rag.embeddings.embed_issue import issue_embed_text, embed_texts
from rag.embeddings.voyage_client import get_embedding_client
from core.config import get_settings


settings = get_settings()
TOKEN = settings.github_pat_key


def ingest_closed_issues(closed_numbers):
    closed_numbers = list(closed_numbers)
    if not closed_numbers:
        return {"promoted": 0, "removed": 0}

    fetched = fetch_closed_issues_by_number(TOKEN, closed_numbers)

    db: Session = SessionLocal()
    try:
        new_issues = []
        for issue in fetched:
            if not issue.fix_summary:
                continue
            exists = db.query(ClosedIssue.github_number).filter(
                ClosedIssue.github_number == issue.github_number
            ).first()
            if exists:
                continue
            new_issues.append(issue)

        if new_issues:
            texts = [issue_embed_text(i.title, i.original_question) for i in new_issues]
            client = get_embedding_client()
            vectors = embed_texts(client, texts)
            rows = [
                ClosedIssue(
                    github_number=i.github_number,
                    title=i.title,
                    original_question=i.original_question,
                    fix_summary=i.fix_summary,
                    url=i.url,
                    closed_at=i.closed_at,
                    tags=i.tags,
                    embeddings=vec,
                )
                for i, vec in zip(new_issues, vectors)
            ]
            db.add_all(rows)

        db.query(OpenIssue).filter(
            OpenIssue.github_number.in_(closed_numbers)
        ).delete(synchronize_session=False)

        db.commit()
        return {"promoted": len(new_issues), "removed": len(closed_numbers)}
    finally:
        db.close()
