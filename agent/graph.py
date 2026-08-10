from langgraph.graph import START, END, StateGraph

from agent.intake.node import intake
from agent.state import AgentState

g = StateGraph(AgentState)

g.add_node("intake", intake)
