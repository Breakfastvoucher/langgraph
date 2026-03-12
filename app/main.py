from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.gateway import ToolGateway
from app.graph import AgentGraphFactory
from app.tools import default_tools

app = FastAPI(title="Xiaoduo Agent PoC", version="0.1.0")


tools = default_tools()
gateway = ToolGateway(tools=tools, allowed_tools=set(tools.keys()))
graph = AgentGraphFactory(gateway).build(enable_checkpointer=False)
checkpoint_graph = AgentGraphFactory(gateway).build(enable_checkpointer=True)


class AgentRequest(BaseModel):
    session_id: str = Field(..., description="Business session ID")
    user_input: str = Field(..., description="User question or task")
    use_checkpointer: bool = Field(False, description="Run with memory checkpointer")


class AgentResponse(BaseModel):
    session_id: str
    response: str
    intent: str
    tool_result: dict


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(req: AgentRequest) -> AgentResponse:
    app_graph = checkpoint_graph if req.use_checkpointer else graph
    config = {"configurable": {"thread_id": req.session_id}}
    state = app_graph.invoke(
        {"session_id": req.session_id, "user_input": req.user_input},
        config=config,
    )
    return AgentResponse(
        session_id=req.session_id,
        response=state["response"],
        intent=state["intent"],
        tool_result=state["tool_result"],
    )
