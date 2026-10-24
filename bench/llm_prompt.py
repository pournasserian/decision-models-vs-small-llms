"""The prompt and JSON schema an LLM gets for the same typed questions a decision model gets.

An LLM answers each question with its pick and a confidence from 0 to 100. It is not asked for a full
distribution: asking open models for 77 decimals under a strict grammar made them loop on digits
(see reports/method.md), and every metric here only needs the top answer and its confidence.
"""

from __future__ import annotations

import json
from typing import Any

from .schema import Answer, Item, Question

SYSTEM = (
    "You answer typed questions about a piece of state. For every question give your answer and your "
    "confidence in it as a whole number from 0 (a guess) to 100 (certain). "
    "Reply with JSON only, matching the schema you are given, with no other text."
)


def render_question(name: str, q: Question) -> str:
    lines = [f"Question \"{name}\" ({q.type}): {q.instructions}"]
    if q.type == "choice":
        lines.append("Options (answer with the option name):")
        for k, v in q.criteria.items():  # type: ignore[union-attr]
            lines.append(f"  - {k}: {v}" if v and v != k else f"  - {k}")
    elif q.type == "score":
        lines.append("Ordered levels, lowest first (answer with the level number):")
        for i, v in enumerate(q.criteria):
            lines.append(f"  - {i}: {v}")
    elif q.criteria:
        lines.append("Answer true or false:")
        lines.append(f"  true: {q.criteria['true']}")  # type: ignore[index]
        lines.append(f"  false: {q.criteria['false']}")  # type: ignore[index]
    else:
        lines.append("Answer true or false.")
    return "\n".join(lines)


def user_message(item: Item) -> str:
    state = item.state if isinstance(item.state, str) else json.dumps(item.state, ensure_ascii=False)
    parts = ["STATE:", state, "", "QUESTIONS:"]
    parts += [render_question(n, q) for n, q in item.questions.items()]
    return "\n".join(parts)


CONFIDENCE = {"type": "integer", "minimum": 0, "maximum": 100}


def json_schema(item: Item) -> dict:
    props: dict[str, Any] = {}
    for name, q in item.questions.items():
        if q.type == "choice":
            answer: dict[str, Any] = {"type": "string", "enum": q.options()}
        elif q.type == "score":
            answer = {"type": "integer", "minimum": 0, "maximum": len(q.criteria) - 1}
        else:
            answer = {"type": "boolean"}
        props[name] = {
            "type": "object",
            "properties": {"answer": answer, "confidence": CONFIDENCE},
            "required": ["answer", "confidence"],
            "additionalProperties": False,
        }
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def max_tokens(item: Item) -> int:
    return 100 + 40 * len(item.questions)


def parse(item: Item, text: str) -> tuple[dict[str, Answer], str | None]:
    """Turn the LLM's JSON into answers. Any problem is a format error; that question then counts as wrong."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        stripped = text.strip().strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:]
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            return {}, "invalid json"
    if not isinstance(data, dict):
        return {}, "not an object"
    answers: dict[str, Answer] = {}
    errors = []
    for name, q in item.questions.items():
        a = data.get(name)
        if not isinstance(a, dict) or "answer" not in a:
            errors.append(f"{name}: missing")
            continue
        opts = q.options()
        try:
            raw = a["answer"]
            if q.type == "noul":
                if isinstance(raw, str):
                    raw = raw.strip().lower() == "true"
                label = "true" if bool(raw) else "false"
            elif q.type == "score":
                label = str(int(raw))
            else:
                label = str(raw)
            if label not in opts:
                errors.append(f"{name}: {raw!r} is not an option")
                continue
            conf = min(max(float(a.get("confidence", 100)), 0.0), 100.0) / 100.0
            # the rest of the mass goes evenly to the other options
            rest = (1.0 - conf) / (len(opts) - 1) if len(opts) > 1 else 0.0
            probs = {o: (conf if o == label else rest) for o in opts}
            answers[name] = Answer(label=label, probabilities=probs, confidence=conf)
        except (TypeError, ValueError) as e:
            errors.append(f"{name}: {e!r}")
    return answers, ("; ".join(errors) if errors else None)
