from typing import Annotated
from operator import add
from typing_extensions import TypedDict


class AgentState(TypedDict):
    github_number: int
    title: str
    original_question: str
    body_summary: str | None
    embedding: list[float] | None
    retrieved: list[dict]
    tool_calls: Annotated[list, add]
    draft: str | None
    needs_escalation: bool