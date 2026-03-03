from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuleBasedLLM:
    """A tiny fallback LLM-like object with an `invoke` method."""

    def invoke(self, prompt: str) -> str:
        return (
            "[RuleBasedLLM Fallback Output]\n"
            "无法访问真实大模型时，系统将根据模板生成结果。\n"
            f"提示词摘要：{prompt[:300]}"
        )
