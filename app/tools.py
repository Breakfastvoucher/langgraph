from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class ToolResult:
    tool_name: str
    success: bool
    data: dict[str, Any]
    message: str


class KnowledgeQueryTool:
    """Template tool: query knowledge base via gateway-friendly boundary."""

    name = "knowledge_query"

    def run(self, query: str, session_id: str) -> ToolResult:
        # TODO: replace with retrieval service call.
        data = {
            "query": query,
            "session_id": session_id,
            "top_k": 3,
            "hits": [
                "PoC 目标：单 Agent + Tool 调用",
                "安全策略：LLM 不可直接访问系统/数据库",
                "架构：FastAPI + LangGraph + Tool Gateway",
            ],
        }
        return ToolResult(
            tool_name=self.name,
            success=True,
            data=data,
            message="Knowledge query completed",
        )


class ReportGeneratorTool:
    """Template tool: generate market/ops report from provided topic."""

    name = "report_generator"

    def run(self, topic: str, session_id: str) -> ToolResult:
        # TODO: replace with report generation pipeline.
        report = (
            f"# 分析报告: {topic}\n"
            "- 背景: 企业智能助手 PoC\n"
            "- 结论: 推荐先固化工具网关与审计日志\n"
            "- 下一步: 扩展多租户认证和异步任务执行\n"
        )
        return ToolResult(
            tool_name=self.name,
            success=True,
            data={"topic": topic, "report_markdown": report, "session_id": session_id},
            message="Report generated",
        )


class TaskLoggerTool:
    """Template tool: persist task activity to audit sink."""

    name = "task_logger"

    def run(self, event: dict[str, Any], session_id: str) -> ToolResult:
        # TODO: replace with external logging service/event bus.
        payload = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
        }
        return ToolResult(
            tool_name=self.name,
            success=True,
            data=payload,
            message="Task log recorded",
        )


def default_tools() -> dict[str, Any]:
    return {
        KnowledgeQueryTool.name: KnowledgeQueryTool(),
        ReportGeneratorTool.name: ReportGeneratorTool(),
        TaskLoggerTool.name: TaskLoggerTool(),
    }
