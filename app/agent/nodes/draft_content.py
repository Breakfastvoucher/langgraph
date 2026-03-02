from __future__ import annotations

from app.agent.prompts.writer_prompt import WRITER_PROMPT
from app.agent.schemas.graph_state import GraphState
from app.agent.tools.style_guide_tool import StyleGuideTool
from app.agent.tools.template_loader_tool import TemplateLoaderTool


async def draft_content(
    state: GraphState,
    llm,
    template_tool: TemplateLoaderTool,
    style_tool: StyleGuideTool,
) -> GraphState:
    template = template_tool.run(state.get("task_type", "default"))
    rules = "\n".join(style_tool.run(state.get("tone", "default")))
    evidence = "\n".join(str(chunk.get("text", "")) for chunk in state.get("retrieved_chunks", []))

    prompt = (
        f"{WRITER_PROMPT}\n\n"
        f"任务类型: {state.get('task_type')}\n"
        f"目标: {state.get('task_goal', '')}\n"
        f"受众: {state.get('audience', '')}\n"
        f"语气规则:\n{rules}\n\n"
        f"模板:\n{template}\n\n"
        f"证据:\n{evidence}\n"
    )
    state["draft"] = await llm.complete(prompt)
    return state
