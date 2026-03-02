from __future__ import annotations

from dataclasses import dataclass

from langgraph.graph import END, StateGraph

from app.agent.nodes.classify_task import classify_task
from app.agent.nodes.collect_requirements import collect_requirements
from app.agent.nodes.compliance_check import compliance_check
from app.agent.nodes.critique_and_rewrite import critique_and_rewrite
from app.agent.nodes.draft_content import draft_content
from app.agent.nodes.finalize_output import finalize_output
from app.agent.nodes.plan_steps import plan_steps
from app.agent.nodes.retrieve_knowledge import retrieve_knowledge
from app.agent.schemas.graph_state import GraphState
from app.agent.tools.kb_search_tool import KBSearchTool
from app.agent.tools.style_guide_tool import StyleGuideTool
from app.agent.tools.template_loader_tool import TemplateLoaderTool


@dataclass(slots=True)
class GraphDependencies:
    llm: object
    kb_tool: KBSearchTool
    template_tool: TemplateLoaderTool
    style_tool: StyleGuideTool


def build_marketing_content_graph(deps: GraphDependencies):
    graph = StateGraph(GraphState)

    graph.add_node("classify_task", classify_task)
    graph.add_node("collect_requirements", collect_requirements)
    graph.add_node("plan_steps", plan_steps)
    graph.add_node("retrieve_knowledge", lambda s: retrieve_knowledge(s, deps.kb_tool))
    graph.add_node(
        "draft_content",
        lambda s: draft_content(s, deps.llm, deps.template_tool, deps.style_tool),
    )
    graph.add_node("critique_and_rewrite", lambda s: critique_and_rewrite(s, deps.llm))
    graph.add_node("compliance_check", lambda s: compliance_check(s, deps.llm))
    graph.add_node("finalize_output", finalize_output)

    graph.set_entry_point("classify_task")

    graph.add_conditional_edges(
        "classify_task",
        lambda s: "fallback" if s.get("fallback_to_qa") else "continue",
        {"fallback": END, "continue": "collect_requirements"},
    )
    graph.add_conditional_edges(
        "collect_requirements",
        lambda s: "need_clarification" if s.get("missing_inputs") else "continue",
        {"need_clarification": END, "continue": "plan_steps"},
    )
    graph.add_edge("plan_steps", "retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "draft_content")
    graph.add_edge("draft_content", "critique_and_rewrite")
    graph.add_conditional_edges(
        "critique_and_rewrite",
        lambda s: "rewrite" if s.get("quality_score", 0) < 18 and s.get("iteration_count", 0) < s.get("max_iterations", 2) else "continue",
        {"rewrite": "draft_content", "continue": "compliance_check"},
    )
    graph.add_edge("compliance_check", "finalize_output")
    graph.add_edge("finalize_output", END)

    return graph.compile()
