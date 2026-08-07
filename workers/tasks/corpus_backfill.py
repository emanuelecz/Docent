from sqlalchemy.orm import Session
import os

from rag.embeddings.embed_issue import embed_texts, issue_embed_text
from database.db import SessionLocal
from database.models.issue import Issue
from ingestion.issues import fetch_closed_issues_page
from rag.embeddings.voyage_client import get_embedding_client
from workers.celery_app import app

client = get_embedding_client()
TOKEN = os.getenv("GITHUB_PAT_KEY")


@app.task(name="backfill_corpus_page")
def backfill_corpus_page(cursor:str | None = None, remaining:int = 1500):
    issues, end_cursor, has_next, rate_limit = fetch_closed_issues_page(TOKEN, cursor)
    db: Session = SessionLocal()
    try:
        filtered = []
        for issue in issues:
            if not issue.fix_summary:
                continue
            exists = db.query(Issue.github_number).filter(Issue.github_number == issue.github_number).first()
            if exists:
                continue
            filtered.append(issue)
        if filtered:
            texts = [issue_embed_text(i) for i in filtered]
            vectors = embed_texts(client, texts)
            
            rows = [
                Issue(
                    github_number= i.github_number,
                    title= i.title,
                    original_question=i.original_question,
                    fix_summary=i.fix_summary,
                    url=i.url,
                    closed_at= i.closed_at,
                    embeddings= vec,
                )
                for i, vec in zip(filtered, vectors)
            ]
            db.add_all(rows)
            db.commit()
            remaining -= len(rows)
    finally:
        db.close()
    
    if has_next and remaining > 0:
        delay = 2
        if rate_limit["remaining"] < 100:
            delay = 60
        backfill_corpus_page.apply_async(
            kwargs={"cursor":end_cursor, "remaining":remaining},
            countdown=delay,
        )