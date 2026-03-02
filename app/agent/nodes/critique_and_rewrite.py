from __future__ import annotations

import re

from app.agent.prompts.critic_prompt import CRITIC_PROMPT
from app.agent.schemas.graph_state import GraphState


async def critique_and_rewrite(state: GraphState, llm) -> GraphState:
    prompt = f"{CRITIC_PROMPT}\n\n当前草稿:\n{state.get('draft', '')}"
    critique = await llm.complete(prompt)

    score = 0
    match = re.search(r"总分\D*(\d{1,2})", critique)
    if match:
        score = int(match.group(1))

    state["critique"] = critique
    state["quality_score"] = score
    state["iteration_count"] = state.get("iteration_count", 0) + 1
    return state
