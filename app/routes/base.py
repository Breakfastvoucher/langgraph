from __future__ import annotations

from typing import Protocol


class BaseRoute(Protocol):
    async def yield_result(self, request_ctx: dict):
        ...
