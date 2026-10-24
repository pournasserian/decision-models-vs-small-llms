from __future__ import annotations

import json

from ..data import parquet_rows, sample
from ..schema import Item, Question

URL = "https://huggingface.co/datasets/LocalLLaMA/typed-decisions/resolve/main/all/test-00000-of-00001.parquet"


def load(n: int | None) -> list[Item]:
    rows = parquet_rows(URL, "typed-decisions-test.parquet")
    items = []
    for r in rows:
        qs = {k: Question(**v) for k, v in json.loads(r["questions"]).items()}
        gold_raw = json.loads(r["gold"])
        gold = {k: str(v["label"]) for k, v in gold_raw.items()}
        soft = {k: {str(o): float(p) for o, p in v["probabilities"].items()} for k, v in gold_raw.items()}
        items.append(Item(id=r["id"], state=json.loads(r["state"]), questions=qs, gold=gold, gold_probabilities=soft))
    return sample(items, n, "typed-decisions")
