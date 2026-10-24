from __future__ import annotations

from ..data import hf_parquet, parquet_rows, sample
from ..schema import Item, Question

REPO = "fancyzhx/ag_news"

CLASSES = ["world", "sports", "business", "science and technology"]

QUESTION = Question(
    type="choice",
    instructions="Which section does this news item belong to?",
    criteria={
        "world": "world news, politics and international affairs",
        "sports": "sports",
        "business": "business, markets and the economy",
        "science and technology": "science and technology",
    },
)


def load(n: int | None) -> list[Item]:
    rows = parquet_rows(hf_parquet(REPO, "default", "test"), "ag-news-test.parquet")
    items = [
        Item(id=f"agnews-{i}", state=r["text"], questions={"section": QUESTION}, gold={"section": CLASSES[r["label"]]})
        for i, r in enumerate(rows)
    ]
    return sample(items, n, "ag-news")
