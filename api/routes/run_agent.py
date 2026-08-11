from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.run import run_agent

router = APIRouter()


class RunRequest(BaseModel):
    github_number: int


@router.post("/agent/run")
async def run_agent_route(payload: RunRequest):
    try:
        final = await run_agent(payload.github_number)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {
        "draft": final["draft"],
        "research_brief": final["research_brief"],
        "needs_escalation": final["needs_escalation"],
        "tool_calls": final["tool_calls"],
    }
