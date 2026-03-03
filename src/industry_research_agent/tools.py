from __future__ import annotations

import os
from typing import Protocol

from .state import KBResult


class InternalKBClient(Protocol):
    def query(self, question: str) -> list[KBResult]:
        """Query internal knowledge base by natural language."""


class StubInternalKBClient:
    """A local stub. Replace with your real SDK or HTTP client in production."""

    def query(self, question: str) -> list[KBResult]:
        return [
            {
                "title": f"内部文档：{question}（样例1）",
                "snippet": "该文档包含市场规模、竞争格局和政策摘要。",
                "score": 0.93,
            },
            {
                "title": f"内部文档：{question}（样例2）",
                "snippet": "该文档包含用户画像、渠道和增长策略信息。",
                "score": 0.88,
            },
        ]


class EnvConfiguredKBClient(StubInternalKBClient):
    """Placeholder for environment-driven KB integration."""

    def query(self, question: str) -> list[KBResult]:
        # In real projects, call your API endpoint with requests/httpx and parse results.
        endpoint = os.getenv("INTERNAL_KB_API_URL")
        if not endpoint:
            return super().query(question)
        return [
            {
                "title": f"来自{endpoint}的文档：{question}",
                "snippet": "请替换该实现以调用真实内部知识库接口。",
                "score": 0.99,
            }
        ]
