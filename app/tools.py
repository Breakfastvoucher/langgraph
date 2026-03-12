from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class KnowledgeQueryInput(BaseModel):
    query: str = Field(..., description="Knowledge query text")
    session_id: str = Field(..., description="Business session id")


class ReportGeneratorInput(BaseModel):
    topic: str = Field(..., description="Report topic")
    session_id: str = Field(..., description="Business session id")


class TaskLoggerInput(BaseModel):
    event: dict[str, Any] = Field(..., description="Structured task event")
    session_id: str = Field(..., description="Business session id")


@tool("knowledge_query", args_schema=KnowledgeQueryInput)
def knowledge_query_tool(query: str, session_id: str) -> dict[str, Any]:
    """Query knowledge base through a gateway-controlled tool interface."""
    # TODO: replace with retrieval service call.
    return {
        "query": query,
        "session_id": session_id,
        "top_k": 3,
        "hits": [
            "PoC 目标：单 Agent + Tool 调用",
            "安全策略：LLM 不可直接访问系统/数据库",
            "架构：FastAPI + LangGraph + Tool Gateway",
        ],
    }


@tool("report_generator", args_schema=ReportGeneratorInput)
def report_generator_tool(topic: str, session_id: str) -> dict[str, Any]:
    """Generate a market/ops report in markdown format."""
    # TODO: replace with report generation pipeline.
    report = (
        f"# 分析报告: {topic}\n"
        "- 背景: 企业智能助手 PoC\n"
        "- 结论: 推荐先固化工具网关与审计日志\n"
        "- 下一步: 扩展多租户认证和异步任务执行\n"
    )
    return {
        "topic": topic,
        "session_id": session_id,
        "report_markdown": report,
    }


@tool("task_logger", args_schema=TaskLoggerInput)
def task_logger_tool(event: dict[str, Any], session_id: str) -> dict[str, Any]:
    """Record task activity into an external audit sink."""
    # TODO: replace with external logging service/event bus.
    return {
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
    }


def default_tools() -> dict[str, Any]:
    return {
        knowledge_query_tool.name: knowledge_query_tool,
        report_generator_tool.name: report_generator_tool,
        task_logger_tool.name: task_logger_tool,
    }
