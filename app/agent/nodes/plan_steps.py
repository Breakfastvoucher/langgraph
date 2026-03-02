from __future__ import annotations

from app.agent.prompts.planner_prompt import PLANNER_PROMPT
from app.agent.schemas.graph_state import GraphState


def plan_steps(state: GraphState) -> GraphState:
    _ = PLANNER_PROMPT
    task_type = state.get("task_type", "unknown")
    plan = [
        f"明确{task_type}目标和目标受众",
        "检索内部知识库中的相关事实与案例",
        "按模板生成结构化初稿",
        "完成质量复审和合规校验",
    ]
    state["plan"] = plan
    return state
