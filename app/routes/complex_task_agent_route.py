from __future__ import annotations

from collections.abc import AsyncGenerator

from app.agent.graphs.marketing_content_graph import build_marketing_content_graph
from app.agent.graphs.marketing_content_graph import GraphDependencies
from app.agent.schemas.graph_state import GraphState
from app.agent.schemas.stream_event import StreamEvent


class ComplexTaskAgentRoute:
    def __init__(self, deps: GraphDependencies) -> None:
        self.graph = build_marketing_content_graph(deps)

    async def yield_result(self, request_ctx: dict) -> AsyncGenerator[StreamEvent, None]:
        state: GraphState = {
            "user_id": request_ctx.get("user_id", ""),
            "session_id": request_ctx.get("session_id", ""),
            "raw_query": request_ctx.get("query", ""),
            "task_goal": request_ctx.get("task_goal", ""),
            "audience": request_ctx.get("audience", ""),
            "tone": request_ctx.get("tone", "professional"),
            "constraints": request_ctx.get("constraints", {}),
            "iteration_count": 0,
            "max_iterations": request_ctx.get("max_iterations", 2),
        }

        yield StreamEvent.stage_update("planning", "已进入复杂任务Agent路由，开始任务分类")
        result = await self.graph.ainvoke(state)

        if result.get("fallback_to_qa"):
            yield StreamEvent.final(
                {
                    "final_answer": "当前请求更适合知识问答路由，请切换到已有意图子类处理。",
                    "citations": [],
                    "quality_score": 0,
                }
            )
            return

        if result.get("missing_inputs"):
            missing = "、".join(result["missing_inputs"])
            yield StreamEvent.final(
                {
                    "final_answer": f"要完成该任务还需要补充：{missing}",
                    "citations": [],
                    "quality_score": 0,
                }
            )
            return

        yield StreamEvent.stage_update("finalizing", "内容已生成，开始流式返回")
        final_answer = result.get("final_answer", "")
        for chunk in self._chunk_text(final_answer, 60):
            yield StreamEvent.token(chunk)

        yield StreamEvent.final(
            {
                "final_answer": final_answer,
                "citations": result.get("citations", []),
                "quality_score": result.get("quality_score", 0),
            }
        )

    @staticmethod
    def _chunk_text(text: str, chunk_size: int) -> list[str]:
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
