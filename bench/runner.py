"""Runs one model over one task, resumably, under the spending cap."""

from __future__ import annotations

import asyncio
import csv
import dataclasses
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from . import clients
from .config import HARD_CAP_USD, LEDGER, RESULTS_DIR, Model
from .schema import Item, Result


def result_path(task: str, model: Model, variant: str = "main") -> Path:
    suffix = "" if variant == "main" else f".{variant}"
    return RESULTS_DIR / task / f"{model.slug}{suffix}.jsonl"


def key(r: dict) -> tuple:
    return (r["item_id"], r.get("repeat", 0), r.get("paraphrase", 0))


def refused(r: dict) -> bool:
    e = r.get("format_error") or ""
    return e.startswith("gave up") or e.startswith("http: 429")


def load_results(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def spent() -> float:
    if not LEDGER.exists():
        return 0.0
    with LEDGER.open(encoding="utf-8") as f:
        return sum(float(row["cost_usd"]) for row in csv.DictReader(f))


def ledger_add(task: str, model: Model, variant: str, n: int, cost: float) -> None:
    new = not LEDGER.exists()
    with LEDGER.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["when_utc", "task", "model", "variant", "requests", "cost_usd"])
        w.writerow([datetime.now(timezone.utc).isoformat(timespec="seconds"), task, model.slug, variant, n, f"{cost:.6f}"])


def to_json(r: Result) -> dict:
    d = dataclasses.asdict(r)
    # the questions are the task's, identical on every row and in bench/tasks/; only the state is kept per row
    if isinstance(d.get("request"), dict):
        d["request"] = {k: v for k, v in d["request"].items() if k not in ("questions", "messages")}
    return d


async def run(
    task: str,
    model: Model,
    items: list[Item],
    variant: str = "main",
    reasoning: dict | None = None,
    repeats: int = 1,
    paraphrases: list[list[Item]] | None = None,
    limit: int | None = None,
) -> list[dict]:
    path = result_path(task, model, variant)
    path.parent.mkdir(parents=True, exist_ok=True)
    # a request the gateway refused (rate limit, outage) is not a measurement: it is redone on the next run
    done = {key(r) for r in load_results(path) if not refused(r)}

    jobs: list[tuple[Item, int, int]] = []
    variants = [items] + (paraphrases or [])
    for p_idx, variant_items in enumerate(variants):
        for rep in range(repeats):
            for it in variant_items:
                if (it.id, rep, p_idx) not in done:
                    jobs.append((it, rep, p_idx))
    if limit is not None:
        jobs = jobs[:limit]
    kept = [r for r in load_results(path) if not refused(r)]
    if len(kept) != len(load_results(path)):
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept), encoding="utf-8")
    if not jobs:
        print(f"[{task}/{model.slug}/{variant}] nothing to do", file=sys.stderr)
        return load_results(path)

    sem = asyncio.Semaphore(model.concurrency)
    lock = asyncio.Lock()
    pace = asyncio.Lock()
    last_sent = [0.0]

    async def paced() -> None:
        if model.min_interval_s <= 0:
            return
        async with pace:
            wait = last_sent[0] + model.min_interval_s - time.monotonic()
            if wait > 0:
                await asyncio.sleep(wait)
            last_sent[0] = time.monotonic()
    total_cost = 0.0
    n_done = 0
    budget_left = HARD_CAP_USD - spent()
    stop = False
    t_start = time.perf_counter()

    out = path.open("a", encoding="utf-8")
    async with httpx.AsyncClient(http2=False) as client:

        async def one(it: Item, rep: int, p_idx: int) -> None:
            nonlocal total_cost, n_done, stop
            async with sem:
                if stop:
                    return
                meta = {"variant": variant, "repeat": rep, "paraphrase": p_idx}
                if reasoning is not None:
                    meta["reasoning"] = reasoning
                delay = 2.0
                attempt = 0
                while True:
                    try:
                        await paced()
                        if model.kind == "chat":
                            res = await clients.call(client, model, it, task, **meta)
                        else:
                            meta.pop("reasoning", None)
                            res = await clients.call(client, model, it, task, **meta)
                        break
                    except httpx.HTTPStatusError as e:
                        # a 4xx the gateway will not change its mind about: record it, do not retry
                        res = Result(it.id, model.slug, task, {}, 0.0, 0.0, None, None, f"http: {e}"[:300], None, None,
                                     variant=variant, repeat=rep, paraphrase=p_idx)
                        break
                    except (clients.RetryableError, httpx.TransportError, httpx.ReadTimeout) as e:
                        reset = getattr(e, "reset_at", None)
                        if reset:
                            # a used-up daily quota is not an outage: wait for its reset, then send the same request again
                            wait = max(reset - time.time(), 0.0) + 30
                            print(f"[{task}/{model.slug}/{variant}] daily quota used up, resuming in {wait / 60:.0f} min",
                                  file=sys.stderr)
                            await asyncio.sleep(wait)
                            continue
                        attempt += 1
                        if attempt == 6:
                            res = Result(it.id, model.slug, task, {}, 0.0, 0.0, None, None, f"gave up: {e}"[:300], None, None,
                                         variant=variant, repeat=rep, paraphrase=p_idx)
                            break
                        ra = getattr(e, "retry_after", None)
                        await asyncio.sleep((ra + 1) if ra else delay + random.random())
                        delay = min(delay * 2, 30)
                async with lock:
                    out.write(json.dumps(to_json(res), ensure_ascii=False) + "\n")
                    out.flush()
                    total_cost += res.cost_usd or 0.0
                    n_done += 1
                    if total_cost > budget_left:
                        stop = True
                        print(f"!! cap of ${HARD_CAP_USD} reached, stopping", file=sys.stderr)
                    if n_done % 50 == 0 or n_done == len(jobs):
                        el = time.perf_counter() - t_start
                        print(f"[{task}/{model.slug}/{variant}] {n_done}/{len(jobs)} ${total_cost:.4f} {el:.0f}s", file=sys.stderr)

        await asyncio.gather(*(one(*j) for j in jobs))
    out.close()

    ledger_add(task, model, variant, n_done, total_cost)
    return load_results(path)
