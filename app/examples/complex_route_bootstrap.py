from __future__ import annotations

from dataclasses import dataclass

from app.agent.graphs.marketing_content_graph import GraphDependencies
from app.agent.tools.kb_search_tool import KBSearchTool
from app.agent.tools.style_guide_tool import StyleGuideTool
from app.agent.tools.template_loader_tool import TemplateLoaderTool
from app.intents.types import IntentType
from app.routes.complex_task_agent_route import ComplexTaskAgentRoute


@dataclass
class DemoLLM:
    async def complete(self, prompt: str) -> str:
        if "总分" in prompt:
            return "评分结果：总分 20。建议补充行动项。"
        return "这是根据内部知识生成的营销内容草稿。"


@dataclass
class DemoRetriever:
    async def search(self, query: str, top_k: int, filters=None):
        return [{"id": "kb-1", "text": f"与 {query} 相关的内部案例", "score": 0.83}]


def create_complex_route() -> ComplexTaskAgentRoute:
    deps = GraphDependencies(
        llm=DemoLLM(),
        kb_tool=KBSearchTool(retriever=DemoRetriever()),
        template_tool=TemplateLoaderTool(
            templates={
                "email": "主题 + 正文 + CTA",
                "report": "摘要 + 数据亮点 + 计划",
                "research": "背景 + 方法 + 发现 + 建议",
                "default": "结构化输出",
            }
        ),
        style_tool=StyleGuideTool(
            tone_rules={
                "professional": ["表达专业", "句子简洁"],
                "default": ["表达清晰"],
            }
        ),
    )
    return ComplexTaskAgentRoute(deps)


def build_route_map():
    return {
        IntentType.COMPLEX_CONTENT_GENERATION: create_complex_route(),
    }
