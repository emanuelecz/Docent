from fastapi import APIRouter, status
from workers.celery_app import app as celery_app

router = APIRouter()

@router.post("/admin/corpus/backfill", status_code=status.HTTP_202_ACCEPTED)
def trigger_backfill(limit:int = 1500):
    task = celery_app.send_task(
        "backfill_corpus_page",
        kwargs={"cursor":None, "remaining": limit}
    )
    return {"status": "accepted", "task_id":task.id, "limit": limit}