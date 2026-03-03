from __future__ import annotations

from textwrap import dedent

from .state import KBResult, ReportState
from .tools import InternalKBClient

MAX_REVISIONS = 2


def planner_node(state: ReportState, llm) -> ReportState:
    topic = state["topic"]
    audience = state.get("audience", "管理层")
    constraints = state.get("constraints", "")
    prompt = dedent(
        f"""
        你是行业研究规划专家，请为主题“{topic}”制定调研报告提纲。
        受众：{audience}
        约束：{constraints or '无'}
        输出要求：
        1. 给出4-6个章节标题（列表）
        2. 给出4-6个关键研究问题（列表）
        """
    ).strip()
    raw = llm.invoke(prompt)

    plan = [
        "行业定义与边界",
        "市场规模与增长驱动",
        "竞争格局与关键玩家",
        "风险与机会",
        "战略建议",
    ]
    questions = [
        f"{topic} 当前市场规模和近3年增速如何？",
        f"{topic} 的主要细分赛道有哪些？",
        f"{topic} 行业内头部企业的差异化优势是什么？",
        f"{topic} 在政策与技术层面有哪些关键风险？",
    ]

    return {
        "plan": plan,
        "research_questions": questions,
        "review_feedback": f"planner原始输出：{raw}",
    }


def researcher_node(state: ReportState, kb_client: InternalKBClient) -> ReportState:
    questions = state.get("research_questions", [])
    results: list[KBResult] = []
    for q in questions:
        docs = kb_client.query(q)
        results.extend(docs)
    return {"kb_results": results}


def writer_node(state: ReportState, llm) -> ReportState:
    topic = state["topic"]
    plan = state.get("plan", [])
    kb_results = state.get("kb_results", [])
    evidence = "\n".join(
        f"- {doc['title']} (score={doc['score']}): {doc['snippet']}" for doc in kb_results[:12]
    )
    prompt = dedent(
        f"""
        你是资深行业分析师，请写一份结构化行业调研报告。
        主题：{topic}
        提纲：{plan}
        证据：
        {evidence or '暂无证据'}
        要求：包含执行摘要、每章分析、结论与建议。
        """
    ).strip()
    draft = llm.invoke(prompt)
    return {"draft_report": draft}


def reviewer_node(state: ReportState, llm) -> ReportState:
    draft = state.get("draft_report", "")
    revision_count = state.get("revision_count", 0)
    prompt = dedent(
        f"""
        请审核以下报告是否满足“逻辑完整、证据充分、建议可执行”。
        若需要修改，输出以 `REVISE:` 开头并给出修改意见；
        若通过，输出以 `APPROVE:` 开头并给出简短结论。

        报告内容：
        {draft}
        """
    ).strip()
    feedback = llm.invoke(prompt)

    approved = feedback.startswith("APPROVE:") or revision_count >= MAX_REVISIONS
    return {
        "review_feedback": feedback,
        "revision_count": revision_count + (0 if approved else 1),
        "final_report": draft if approved else "",
    }


def route_after_review(state: ReportState) -> str:
    if state.get("final_report"):
        return "end"
    return "writer"
