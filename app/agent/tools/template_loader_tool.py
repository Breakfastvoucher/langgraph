from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TemplateLoaderTool:
    templates: dict[str, str]

    def run(self, task_type: str) -> str:
        return self.templates.get(task_type, self.templates.get("default", ""))
