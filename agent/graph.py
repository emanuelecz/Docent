from langgraph.graph import START, END, StateGraph

from agent.state import AgentState
from agent.intake.node import intake
from agent.research.node import research, finalize_research
from agent.research.tools import tools_node
from agent.research.edges import should_continue
from agent.draft.node import draft

g = StateGraph(AgentState)

g.add_node("intake", intake)
g.add_node("research", research)
g.add_node("tools", tools_node)
g.add_node("finalize_research", finalize_research)
g.add_node("draft", draft)

g.add_edge(START, "intake")
g.add_edge("intake", "research")
g.add_conditional_edges(
    "research",
    should_continue,
    {"tools": "tools", "finalize": "finalize_research"},
)
g.add_edge("tools", "research")
g.add_edge("finalize_research", "draft")
g.add_edge("draft", END)

graph = g.compile()
