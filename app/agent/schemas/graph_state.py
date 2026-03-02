from __future__ import annotations

from typing import Any, Literal, TypedDict

TaskType = Literal["email", "report", "research", "unknown"]


class GraphState(TypedDict, total=False):
    user_id: str
    session_id: str
    raw_query: str

    task_type: TaskType
    task_goal: str
    audience: str
    tone: str

    constraints: dict[str, Any]
    required_inputs: list[str]
    missing_inputs: list[str]

    plan: list[str]
    retrieved_chunks: list[dict[str, Any]]
    citations: list[str]

    draft: str
    critique: str
    quality_score: int
    final_answer: str

    iteration_count: int
    max_iterations: int
    fallback_to_qa: bool
