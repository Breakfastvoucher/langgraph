from __future__ import annotations

from app.agent.prompts.compliance_prompt import COMPLIANCE_PROMPT
from app.agent.schemas.graph_state import GraphState


async def compliance_check(state: GraphState, llm) -> GraphState:
    prompt = f"{COMPLIANCE_PROMPT}\n\n待检查内容:\n{state.get('draft', '')}"
    result = await llm.complete(prompt)

    state["constraints"] = {**state.get("constraints", {}), "compliance_report": result}
    return state
