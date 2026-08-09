from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models.open_issue import OpenIssue
from ingestion.issues import fetch_all_open_issues
from workers.celery_app import app
from rag.ingestion.issues import ingest_closed_issues
from core.config import get_settings


settings = get_settings()
TOKEN = settings.github_pat_key


@app.task(name="poll_open_issues")
def poll_open_issues():
    fetched = fetch_all_open_issues(TOKEN)
    fetched_by_number = {i.github_number: i for i in fetched}
    fetched_numbers = set(fetched_by_number)

    db: Session = SessionLocal()
    try:
        saved_numbers = {number for (number,) in db.query(OpenIssue.github_number).all()}

        new_numbers = fetched_numbers - saved_numbers      
        closed_numbers = saved_numbers - fetched_numbers   

        new_issues = [fetched_by_number[n] for n in new_numbers]
        if new_issues:
            db.add_all(
                OpenIssue(
                    github_number=i.github_number,
                    original_question=i.original_question,
                    title=i.title,
                    url=i.url,
                    tags=i.tags,
                )
                for i in new_issues
            )
            db.commit()

        ingest_closed_issues(closed_numbers)

        return {
            "open_total": len(fetched_numbers),
            "new": len(new_issues),
            "closed": len(closed_numbers),
        }
    finally:
        db.close()
