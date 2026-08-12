from langchain_core.messages import SystemMessage, HumanMessage

from core.config import get_settings
from agent.state import AgentState
from agent.research.research_llm import get_research_llm


def _render_brief(brief: dict) -> str:
    refs = brief.get("corpus_references") or []
    ref_lines = "\n".join(
        f"- #{r.get('github_number')} {r.get('url')} — {r.get('why_relevant')}"
        for r in refs
    ) or "none"

    findings = brief.get("external_finding") or []
    finding_lines = "\n".join(f"- {f}" for f in findings) or "none"

    open_qs = brief.get("open_questions") or []
    open_lines = "\n".join(f"- {q}" for q in open_qs) or "none"

    return (
        f"Problem: {brief.get('problem_restatement', '')}\n"
        f"Likely cause: {brief.get('root_cause_hypothesis', '')}\n"
        f"Suggested direction: {brief.get('suggested_response_direction', '')}\n"
        f"Confidence: {brief.get('confidence', 'unknown')}\n"
        f"Needs escalation: {brief.get('needs_escalation', False)}\n"
        f"Similar resolved issues:\n{ref_lines}\n"
        f"External findings:\n{finding_lines}\n"
        f"Open questions:\n{open_lines}"
    )


async def draft(state: AgentState) -> dict:
    settings = get_settings()
    repo = f"{settings.repo_owner}/{settings.repo_name}"
    brief = state.get("research_brief") or {}

    system = SystemMessage(content=settings.prompts.draft_system_prompt.format(repo=repo))
    user = HumanMessage(
        content=settings.prompts.draft_user_template.format(
            title=state["title"],
            original_question=state["original_question"],
            brief=_render_brief(brief),
        )
    )

    llm = get_research_llm()
    resp = await llm.ainvoke([system, user])
    return {"draft": resp.content}
