from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class MilvusRetriever(Protocol):
    async def search(self, query: str, top_k: int, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        ...


@dataclass(slots=True)
class KBSearchTool:
    retriever: MilvusRetriever

    async def run(self, query: str, top_k: int = 6, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return await self.retriever.search(query=query, top_k=top_k, filters=filters)
