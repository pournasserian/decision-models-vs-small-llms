"""Accuracy with a confidence interval, Brier score, calibration error, format failures, latency and cost."""

from __future__ import annotations

import math
import statistics
from collections import Counter
from dataclasses import dataclass

from .schema import Item


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (centre - half, centre + half)


def majority_baseline(items: list[Item]) -> float:
    """Accuracy of always answering each question's most common gold label."""
    per_q: dict[str, Counter] = {}
    for it in items:
        for q, g in it.gold.items():
            per_q.setdefault(q, Counter())[g] += 1
    hits = sum(c.most_common(1)[0][1] for c in per_q.values())
    total = sum(sum(c.values()) for c in per_q.values())
    return hits / total if total else 0.0


@dataclass
class Summary:
    model: str
    task: str
    n_items: int
    n_decisions: int
    n_answered: int
    accuracy: float
    ci_low: float
    ci_high: float
    brier: float | None
    ece: float | None
    format_failures: int
    latency_p50_ms: float | None
    latency_p95_ms: float | None
    cost_usd: float
    cost_per_1k_decisions: float | None
    input_tokens: int
    output_tokens: int
    per_type: dict[str, tuple[int, int]]  # type -> (correct, total)
    soft_agreement: float | None = None  # accuracy against the soft gold's argmax where the dataset has one
    kl_from_gold: float | None = None


def summarise(items: list[Item], results: list[dict], model: str, task: str) -> Summary:
    by_id = {it.id: it for it in items}
    main = [r for r in results if r.get("repeat", 0) == 0 and r.get("paraphrase", 0) == 0 and r["item_id"] in by_id]
    n_decisions = sum(len(by_id[r["item_id"]].questions) for r in main)
    correct = 0
    answered = 0
    brier_terms: list[float] = []
    conf_pairs: list[tuple[float, int]] = []
    kl_terms: list[float] = []
    per_type: dict[str, list[int]] = {}
    failures = 0
    latencies = []
    cost = 0.0
    in_tok = out_tok = 0
    for r in main:
        it = by_id[r["item_id"]]
        if r.get("format_error"):
            failures += 1
        if r.get("latency_ms"):
            latencies.append(r["latency_ms"])
        cost += r.get("cost_usd") or 0.0
        in_tok += r.get("input_tokens") or 0
        out_tok += r.get("output_tokens") or 0
        for qname, q in it.questions.items():
            gold = it.gold[qname]
            pt = per_type.setdefault(q.type, [0, 0])
            pt[1] += 1
            a = (r.get("answers") or {}).get(qname)
            if not a or a.get("label") is None:
                continue  # unanswered counts as wrong
            answered += 1
            probs = a["probabilities"]
            hit = a["label"] == gold
            correct += hit
            pt[0] += hit
            # top-1 Brier: the confidence in the chosen answer against whether it was right.
            # Decision models give a full distribution and LLMs only a confidence, so this is the one
            # calibration measure both can be scored on.
            conf = float(a.get("confidence") if a.get("confidence") is not None else max(probs.values()))
            brier_terms.append((conf - (1.0 if hit else 0.0)) ** 2)
            conf_pairs.append((conf, int(hit)))
            soft = it.gold_probabilities.get(qname)
            if soft:
                eps = 1e-6
                kl_terms.append(
                    sum(
                        soft.get(o, 0.0) * math.log((soft.get(o, 0.0) + eps) / (probs.get(o, 0.0) + eps))
                        for o in q.options()
                    )
                )
    acc = correct / n_decisions if n_decisions else 0.0
    lo, hi = wilson(correct, n_decisions)
    ece = None
    if conf_pairs:
        bins: dict[int, list[tuple[float, int]]] = {}
        for c, h in conf_pairs:
            bins.setdefault(min(int(c * 10), 9), []).append((c, h))
        ece = sum(
            len(b) / len(conf_pairs) * abs(statistics.fmean(h for _, h in b) - statistics.fmean(c for c, _ in b))
            for b in bins.values()
        )
    return Summary(
        model=model,
        task=task,
        n_items=len(main),
        n_decisions=n_decisions,
        n_answered=answered,
        accuracy=acc,
        ci_low=lo,
        ci_high=hi,
        brier=statistics.fmean(brier_terms) if brier_terms else None,
        ece=ece,
        format_failures=failures,
        latency_p50_ms=statistics.median(latencies) if latencies else None,
        latency_p95_ms=sorted(latencies)[int(0.95 * (len(latencies) - 1))] if latencies else None,
        cost_usd=cost,
        cost_per_1k_decisions=(cost / n_decisions * 1000) if n_decisions else None,
        input_tokens=in_tok,
        output_tokens=out_tok,
        per_type={t: (c, n) for t, (c, n) in per_type.items()},
        kl_from_gold=statistics.fmean(kl_terms) if kl_terms else None,
    )


def consistency(items: list[Item], results: list[dict]) -> dict:
    """Agreement across repeats and across paraphrases: how often every run of one item gave the same label."""
    by_id = {it.id: it for it in items}
    groups: dict[tuple[str, str, int], list[str | None]] = {}  # (item, question, paraphrase) -> labels over repeats
    para: dict[tuple[str, str], list[str | None]] = {}  # (item, question) -> labels over paraphrases (repeat 0)
    for r in results:
        it = by_id.get(r["item_id"])
        if not it:
            continue
        for qname in it.questions:
            a = (r.get("answers") or {}).get(qname) or {}
            label = a.get("label")
            groups.setdefault((it.id, qname, r.get("paraphrase", 0)), []).append(label)
            if r.get("repeat", 0) == 0:
                para.setdefault((it.id, qname), []).append(label)
    rep_groups = [g for g in groups.values() if len(g) > 1]
    par_groups = [g for g in para.values() if len(g) > 1]
    return {
        "repeat_groups": len(rep_groups),
        "repeat_agreement": statistics.fmean(len(set(g)) == 1 for g in rep_groups) if rep_groups else None,
        "paraphrase_groups": len(par_groups),
        "paraphrase_agreement": statistics.fmean(len(set(g)) == 1 for g in par_groups) if par_groups else None,
    }
