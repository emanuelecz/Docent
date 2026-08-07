from celery import Celery
import os

app = Celery(
    "Docent",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["workers.tasks.corpus_backfill", "workers.tasks.github_poller"],
)

app.conf.beat_schedule = {
    "poll-github-issues": {
        "task": "poll_github_issues",
        "schedule": 300.0,  
    }
}
