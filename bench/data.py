from __future__ import annotations

import json
import random
from pathlib import Path

import httpx
import pyarrow.parquet as pq

from .config import DATA_DIR, SEED

HF = "https://huggingface.co"


def fetch(url: str, name: str) -> Path:
    """Download a dataset file once into data/ and return its path."""
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / name
    if path.exists():
        return path
    with httpx.Client(follow_redirects=True, timeout=120) as client:
        r = client.get(url)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def parquet_rows(url: str, name: str) -> list[dict]:
    return pq.read_table(fetch(url, name)).to_pylist()


def jsonl_rows(url: str, name: str) -> list[dict]:
    return [json.loads(line) for line in fetch(url, name).read_text(encoding="utf-8").splitlines() if line.strip()]


def sample(rows: list, n: int | None, salt: str) -> list:
    """A fixed random sample, the same on every machine, so a rerun scores the same items."""
    if n is None or n >= len(rows):
        return list(rows)
    rng = random.Random(f"{SEED}:{salt}")
    idx = sorted(rng.sample(range(len(rows)), n))
    return [rows[i] for i in idx]


def hf_parquet(repo: str, config: str, split: str) -> str:
    return f"{HF}/api/datasets/{repo}/parquet/{config}/{split}/0.parquet"
