from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ToolGateway:
    """Single enforcement point for all external operations."""

    tools: dict[str, Any]
    allowed_tools: set[str]

    def invoke(self, tool_name: str, payload: dict[str, Any], session_id: str) -> dict[str, Any]:
        if tool_name not in self.allowed_tools:
            return {
                "tool_name": tool_name,
                "success": False,
                "message": f"Tool '{tool_name}' is not allowed",
                "data": {"reason": "forbidden"},
            }

        tool = self.tools.get(tool_name)
        if tool is None:
            return {
                "tool_name": tool_name,
                "success": False,
                "message": f"Tool '{tool_name}' not registered",
                "data": {"reason": "not_found"},
            }

        try:
            # @tool tools are invoked with normalized payload including session_id.
            tool_data = tool.invoke({**payload, "session_id": session_id})
            return {
                "tool_name": tool_name,
                "success": True,
                "message": "Tool execution completed",
                "data": tool_data,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "tool_name": tool_name,
                "success": False,
                "message": f"Tool execution failed: {exc}",
                "data": {"reason": "execution_error"},
            }
