from langchain_core.messages import SystemMessage, HumanMessage

from core.config import get_settings
from agent.state import AgentState
from agent.research.research_llm import get_research_llm


async def draft(state: AgentState) -> dict:
    settings = get_settings()
    repo = f"{settings.repo_owner}/{settings.repo_name}"
    system = SystemMessage(content=settings.prompts.draft_system_prompt.format(repo=repo))
    user = HumanMessage(
        content=settings.prompts.draft_user_template.format(brief=state.get("research_brief") or {})
    )

    llm = get_research_llm()
    resp = await llm.ainvoke([system, user])
    return {"draft": resp.content}
