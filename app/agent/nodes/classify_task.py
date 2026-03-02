from __future__ import annotations

from app.agent.schemas.graph_state import GraphState


def classify_task(state: GraphState) -> GraphState:
    query = state.get("raw_query", "")
    lowered = query.lower()

    mapping = {
        "邮件": "email",
        "email": "email",
        "汇报": "report",
        "周报": "report",
        "月报": "report",
        "调研": "research",
        "报告": "research",
    }

    task_type = "unknown"
    for key, value in mapping.items():
        if key in lowered or key in query:
            task_type = value
            break

    state["task_type"] = task_type
    state["fallback_to_qa"] = task_type == "unknown"
    return state
