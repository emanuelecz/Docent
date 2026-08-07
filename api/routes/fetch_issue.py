from fastapi import APIRouter
from ingestion.issues import fetch_latest_open_issue
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("GITHUB_PAT_KEY")

router = APIRouter()


@router.post("/issues/fetch")
def fetch_open_issue():
    issue = fetch_latest_open_issue(TOKEN)
    if issue is None:
        return {"status": "empty", "message": "No open issue available at the moment"}
    return {"status": "success", "issue": issue}
