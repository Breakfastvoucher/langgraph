from __future__ import annotations

from typing import Any, Literal, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.gateway import ToolGateway


Intent = Literal["knowledge_query", "report_generator", "task_logger"]


class AgentState(TypedDict, total=False):
    session_id: str
    user_input: str
    intent: Intent
    tool_payload: dict[str, Any]
    tool_result: dict[str, Any]
    response: str


class AgentGraphFactory:
    def __init__(self, gateway: ToolGateway):
        self.gateway = gateway

    def user_input_node(self, state: AgentState) -> AgentState:
        return state

    def intent_classification_node(self, state: AgentState) -> AgentState:
        text = state["user_input"].lower()
        if any(word in text for word in ["报告", "report", "分析"]):
            intent: Intent = "report_generator"
        elif any(word in text for word in ["日志", "log", "记录"]):
            intent = "task_logger"
        else:
            intent = "knowledge_query"

        payload = self._build_payload(intent, state["user_input"])
        return {"intent": intent, "tool_payload": payload}

    def decision_node(self, state: AgentState) -> AgentState:
        return state

    def tool_node(self, state: AgentState) -> AgentState:
        result = self.gateway.invoke(
            tool_name=state["intent"],
            payload=state["tool_payload"],
            session_id=state["session_id"],
        )
        return {
            "tool_result": {
                "tool_name": result.tool_name,
                "success": result.success,
                "message": result.message,
                "data": result.data,
            }
        }

    def response_node(self, state: AgentState) -> AgentState:
        tool_result = state["tool_result"]
        if not tool_result["success"]:
            return {"response": f"请求失败: {tool_result['message']}"}

        response = (
            f"session={state['session_id']}\n"
            f"intent={state['intent']}\n"
            f"tool={tool_result['tool_name']}\n"
            f"message={tool_result['message']}\n"
            f"data={tool_result['data']}"
        )
        return {"response": response}

    def build(self, enable_checkpointer: bool = False):
        graph = StateGraph(AgentState)
        graph.add_node("user_input", self.user_input_node)
        graph.add_node("intent_classification", self.intent_classification_node)
        graph.add_node("decision", self.decision_node)
        graph.add_node("tool", self.tool_node)
        graph.add_node("response", self.response_node)

        graph.add_edge(START, "user_input")
        graph.add_edge("user_input", "intent_classification")
        graph.add_edge("intent_classification", "decision")
        graph.add_edge("decision", "tool")
        graph.add_edge("tool", "response")
        graph.add_edge("response", END)

        checkpointer = MemorySaver() if enable_checkpointer else None
        return graph.compile(checkpointer=checkpointer)

    @staticmethod
    def _build_payload(intent: Intent, user_input: str) -> dict[str, Any]:
        if intent == "knowledge_query":
            return {"query": user_input}
        if intent == "report_generator":
            return {"topic": user_input}
        return {"event": {"type": "user_request", "content": user_input}}
