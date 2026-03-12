from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.tools import ToolResult


@dataclass(slots=True)
class ToolGateway:
    """Single enforcement point for all external operations."""

    tools: dict[str, Any]
    allowed_tools: set[str]

    def invoke(self, tool_name: str, payload: dict[str, Any], session_id: str) -> ToolResult:
        if tool_name not in self.allowed_tools:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                data={"reason": "forbidden"},
                message=f"Tool '{tool_name}' is not allowed",
            )
        tool = self.tools.get(tool_name)
        if tool is None:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                data={"reason": "not_found"},
                message=f"Tool '{tool_name}' not registered",
            )

        # Gateway controls normalized interface to avoid direct host access by LLM.
        if tool_name == "knowledge_query":
            return tool.run(query=payload["query"], session_id=session_id)
        if tool_name == "report_generator":
            return tool.run(topic=payload["topic"], session_id=session_id)
        if tool_name == "task_logger":
            return tool.run(event=payload["event"], session_id=session_id)

        return ToolResult(
            tool_name=tool_name,
            success=False,
            data={"reason": "unsupported_interface"},
            message=f"Tool '{tool_name}' does not implement gateway mapping",
        )
