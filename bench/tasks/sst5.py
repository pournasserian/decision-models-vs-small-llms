from __future__ import annotations

from ..data import jsonl_rows, sample
from ..schema import Item, Question

URL = "https://huggingface.co/datasets/SetFit/sst5/resolve/main/test.jsonl"

LEVELS = ["very negative", "negative", "neutral", "positive", "very positive"]

QUESTION = Question(
    type="score",
    instructions="How positive is the sentiment of this movie review sentence?",
    criteria=LEVELS,
)


def load(n: int | None) -> list[Item]:
    rows = jsonl_rows(URL, "sst5-test.jsonl")
    items = [
        Item(id=f"sst5-{i}", state=r["text"], questions={"sentiment": QUESTION}, gold={"sentiment": str(r["label"])})
        for i, r in enumerate(rows)
    ]
    return sample(items, n, "sst5")
