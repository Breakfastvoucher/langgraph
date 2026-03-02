from __future__ import annotations

from enum import StrEnum


class IntentType(StrEnum):
    COMPLEX_CONTENT_GENERATION = "complex_content_generation"
    KNOWLEDGE_QA = "knowledge_qa"
