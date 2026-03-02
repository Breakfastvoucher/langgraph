from __future__ import annotations

from app.agent.schemas.graph_state import GraphState


def finalize_output(state: GraphState) -> GraphState:
    report = state.get("constraints", {}).get("compliance_report", "")
    final_text = state.get("draft", "")
    if report:
        final_text = f"{final_text}\n\n[合规检查]\n{report}"

    state["final_answer"] = final_text
    return state
