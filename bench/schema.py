from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

QuestionType = Literal["choice", "score", "noul"]


@dataclass
class Question:
    """One typed question in TypeSafe's System One shape, the shape every model here gets."""

    type: QuestionType
    instructions: str
    # choice: {option: guidance}; noul: {"true": ..., "false": ...}; score: [level 0, level 1, ...]
    criteria: dict[str, str] | list[str] | None = None

    def options(self) -> list[str]:
        if self.type == "score":
            return [str(i) for i in range(len(self.criteria))]
        if self.type == "noul":
            return ["true", "false"]
        return list(self.criteria.keys())  # type: ignore[union-attr]

    def to_wire(self) -> dict[str, Any]:
        w: dict[str, Any] = {"type": self.type, "instructions": self.instructions}
        if self.criteria is not None:
            w["criteria"] = self.criteria
        return w


@dataclass
class Item:
    id: str
    state: str | dict | list
    questions: dict[str, Question]
    # gold label per question: an option key, a level index as a string, or "true"/"false"
    gold: dict[str, str]
    # soft gold where the dataset has one (typed-decisions), else empty
    gold_probabilities: dict[str, dict[str, float]] = field(default_factory=dict)


@dataclass
class Answer:
    label: str | None
    probabilities: dict[str, float]
    confidence: float | None = None


@dataclass
class Result:
    item_id: str
    model: str
    task: str
    answers: dict[str, Answer]
    latency_ms: float
    cost_usd: float | None
    input_tokens: int | None
    output_tokens: int | None
    format_error: str | None
    raw: Any
    request: Any
    variant: str = "main"
    repeat: int = 0
    paraphrase: int = 0
