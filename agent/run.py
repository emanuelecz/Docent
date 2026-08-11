from database.db import SessionLocal
from database.models.open_issue import OpenIssue
from agent.graph import graph
from agent.state import AgentState


async def run_agent(github_number: int) -> AgentState:
    db = SessionLocal()
    try:
        issue = db.query(OpenIssue).filter(OpenIssue.github_number == github_number).first()
        if issue is None:
            raise ValueError(f"Open issue #{github_number} not found")
        title, original_question = issue.title, issue.original_question
    finally:
        db.close()

    initial: AgentState = {
        "github_number": github_number,
        "title": title,
        "original_question": original_question,
        "body_summary": None,
        "embedding": None,
        "retrieved": [],
        "tool_calls": [],
        "draft": None,
        "needs_escalation": False,
        "messages": [],
        "research_brief": None,
        "research_iterations": 0,
        "rag_used": False,
    }
    return await graph.ainvoke(initial)
