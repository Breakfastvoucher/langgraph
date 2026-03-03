from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .llm import RuleBasedLLM
from .nodes import (
    planner_node,
    researcher_node,
    reviewer_node,
    route_after_review,
    writer_node,
)
from .state import ReportState
from .tools import EnvConfiguredKBClient, InternalKBClient


def build_report_graph(llm=None, kb_client: InternalKBClient | None = None):
    llm = llm or RuleBasedLLM()
    kb_client = kb_client or EnvConfiguredKBClient()

    graph = StateGraph(ReportState)

    graph.add_node("planner", lambda s: planner_node(s, llm))
    graph.add_node("researcher", lambda s: researcher_node(s, kb_client))
    graph.add_node("writer", lambda s: writer_node(s, llm))
    graph.add_node("reviewer", lambda s: reviewer_node(s, llm))

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_conditional_edges(
        "reviewer",
        route_after_review,
        {
            "writer": "writer",
            "end": END,
        },
    )

    return graph.compile()
