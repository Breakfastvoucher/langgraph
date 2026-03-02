from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class StreamEvent:
    event_type: str
    stage: str | None = None
    message: str | None = None
    content: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def stage_update(cls, stage: str, message: str) -> "StreamEvent":
        return cls(event_type="stage_update", stage=stage, message=message)

    @classmethod
    def token(cls, content: str) -> "StreamEvent":
        return cls(event_type="token", content=content)

    @classmethod
    def final(cls, payload: dict[str, Any]) -> "StreamEvent":
        return cls(event_type="final", payload=payload)
