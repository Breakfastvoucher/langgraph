from __future__ import annotations

from app.agent.schemas.graph_state import GraphState
from app.agent.tools.kb_search_tool import KBSearchTool


async def retrieve_knowledge(state: GraphState, kb_tool: KBSearchTool) -> GraphState:
    chunks = await kb_tool.run(query=state.get("raw_query", ""), top_k=6)
    state["retrieved_chunks"] = chunks
    state["citations"] = [str(item.get("id", "unknown")) for item in chunks]
    return state
