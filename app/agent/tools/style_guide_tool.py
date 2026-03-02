from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class StyleGuideTool:
    tone_rules: dict[str, list[str]]

    def run(self, tone: str) -> list[str]:
        return self.tone_rules.get(tone, self.tone_rules.get("default", []))
