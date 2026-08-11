from typing import Annotated
from operator import add
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage




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
    messages: Annotated[list[AnyMessage], add_messages]
    research_brief: dict | None
    research_iterations: int
    rag_used: bool
    