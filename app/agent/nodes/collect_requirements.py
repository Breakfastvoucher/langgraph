from __future__ import annotations

from app.agent.schemas.graph_state import GraphState


def collect_requirements(state: GraphState) -> GraphState:
    required_by_type = {
        "email": ["task_goal", "audience", "tone"],
        "report": ["task_goal", "audience"],
        "research": ["task_goal", "constraints"],
        "unknown": ["task_goal"],
    }
    required = required_by_type.get(state.get("task_type", "unknown"), ["task_goal"])
    missing = [field for field in required if not state.get(field)]

    state["required_inputs"] = required
    state["missing_inputs"] = missing
    return state
