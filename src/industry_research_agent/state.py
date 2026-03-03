from typing import Annotated, TypedDict


class KBResult(TypedDict):
    title: str
    snippet: str
    score: float


class ReportState(TypedDict, total=False):
    topic: str
    audience: str
    constraints: str
    plan: list[str]
    research_questions: list[str]
    kb_results: Annotated[list[KBResult], list.__add__]
    draft_report: str
    review_feedback: str
    final_report: str
    revision_count: int
