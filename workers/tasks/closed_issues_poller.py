import os

from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models.closed_issue import ClosedIssue
from ingestion.issues import fetch_closed_issues_page
from rag.embeddings.embed_issue import embed_texts, issue_embed_text
from rag.embeddings.voyage_client import get_embedding_client
from workers.celery_app import app

TOKEN = os.getenv("GITHUB_PAT_KEY")


@app.task(name="poll_github_issues")
def poll_github_issues():
    issues, _end_cursor, _has_next, _rate_limit = fetch_closed_issues_page(TOKEN, cursor=None)

    db: Session = SessionLocal()
    try:
        new_issues = []
        for issue in issues:
            exists = db.query(ClosedIssue.github_number).filter(
                ClosedIssue.github_number == issue.github_number
            ).first()
            if exists:
                break
            if not issue.fix_summary:
                continue
            new_issues.append(issue)

        if not new_issues:
            return {"new_issues": 0}

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
        db.commit()
        return {"new_issues": len(rows)}
    finally:
        db.close()
