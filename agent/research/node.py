from langchain_core.messages import SystemMessage, HumanMessage

from core.config import get_settings
from agent.state import AgentState
from agent.research.research_llm import get_research_llm
from agent.research.tools import search_corpus
from agent.research.github_mcp import get_github_tools
from schemas.research import ResearchBrief


def _system_message() -> SystemMessage:
    settings = get_settings()
    repo = f"{settings.repo_owner}/{settings.repo_name}"
    return SystemMessage(content=settings.prompts.research_system_prompt.format(repo=repo))


async def research(state: AgentState) -> dict:
    settings = get_settings()
    iterations = state.get("research_iterations", 0)
    at_cap = iterations >= settings.research_max_iterations

    tools = []
    if not at_cap:
        if not state.get("rag_used", False):
            tools.append(search_corpus)
        tools.extend(await get_github_tools())

    llm = get_research_llm()
    bound = llm.bind_tools(tools) if tools else llm

    history = list(state["messages"])
    seed = []
    if not history:
        seed = [
            HumanMessage(
                content=settings.prompts.research_user_template.format(
                    github_number=state["github_number"],
                    title=state["title"],
                    body_summary=state["body_summary"] or state["original_question"],
                )
            )
        ]
        history = seed

    ai = await bound.ainvoke([_system_message(), *history])
    return {"messages": [*seed, ai], "research_iterations": iterations + 1}


async def finalize_research(state: AgentState) -> dict:
    settings = get_settings()
    llm = get_research_llm().with_structured_output(ResearchBrief)
    instruction = HumanMessage(content=settings.prompts.research_finalize_instruction)
    brief = await llm.ainvoke([_system_message(), *state["messages"], instruction])
    return {"research_brief": brief.model_dump(), "needs_escalation": brief.needs_escalation}
