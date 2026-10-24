"""Writes reports/: one Markdown file per task, a summary across tasks, and the ledger as a table."""

from __future__ import annotations

import csv
import json
from datetime import date

from . import tasks
from .config import LEDGER, MODELS, REPORTS_DIR, Model
from .metrics import Summary, consistency, majority_baseline, summarise
from .runner import load_results, result_path


def pct(x: float | None, digits: int = 1) -> str:
    return "–" if x is None else f"{100 * x:.{digits}f}%"


def num(x: float | None, digits: int = 3) -> str:
    return "–" if x is None else f"{x:.{digits}f}"


def ms(x: float | None) -> str:
    return "–" if x is None else f"{x:,.0f} ms"


def usd(x: float | None, digits: int = 4) -> str:
    return "–" if x is None else f"${x:.{digits}f}"


def task_report(task: str) -> tuple[str, dict[str, Summary]]:
    loader, default_n, desc, cite = tasks.TASKS[task]
    items = tasks.load(task)
    base = majority_baseline(items)
    n_dec = sum(len(it.questions) for it in items)
    lines = [f"# {task}", "", f"{desc}.", "", f"Data: {cite}. {len(items)} items, {n_dec} decisions. "
             f"Majority-class baseline: {pct(base)}.", ""]
    summaries: dict[str, Summary] = {}
    rows = []
    for slug, model in MODELS.items():
        results = load_results(result_path(task, model))
        if not results:
            continue
        s = summarise(items, results, slug, task)
        summaries[slug] = s
        rows.append(s)
    rows.sort(key=lambda s: -s.accuracy)
    lines += [
        "| Model | Kind | Accuracy | 95% CI | Brier (top-1) | ECE | Format failures | p50 | p95 | Cost | Per 1k decisions |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in rows:
        m = MODELS[s.model]
        lines.append(
            f"| {m.name} | {m.family} | {pct(s.accuracy)} | {pct(s.ci_low)} to {pct(s.ci_high)} | {num(s.brier)} | "
            f"{num(s.ece)} | {s.format_failures} of {s.n_items} | {ms(s.latency_p50_ms)} | {ms(s.latency_p95_ms)} | "
            f"{usd(s.cost_usd)} | {usd(s.cost_per_1k_decisions, 3)} |"
        )
    lines.append(f"| Majority class | baseline | {pct(base)} | | | | | | | | |")
    types = sorted({t for s in rows for t in s.per_type})
    if len(types) > 1:
        lines += ["", "## By question type", "", "| Model | " + " | ".join(types) + " |", "|---|" + "---|" * len(types)]
        for s in rows:
            cells = []
            for t in types:
                c, n = s.per_type.get(t, (0, 0))
                cells.append(f"{pct(c / n) if n else '–'} ({n})")
            lines.append(f"| {MODELS[s.model].name} | " + " | ".join(cells) + " |")
    if any(s.kl_from_gold is not None for s in rows):
        lines += ["", "## Against the soft gold", "",
                  "KL divergence from the benchmark's gold distribution, for the models that return one.", "",
                  "| Model | KL from gold |", "|---|---|"]
        for s in rows:
            if s.kl_from_gold is not None:
                lines.append(f"| {MODELS[s.model].name} | {num(s.kl_from_gold)} |")
    # consistency and the reasoning variant, where they were run
    extra = []
    for slug, model in MODELS.items():
        rep = load_results(result_path(task, model, "repeats"))
        if rep:
            c = consistency(items, rep)
            extra.append(f"| {model.name} | repeats | {pct(c['repeat_agreement'])} over {c['repeat_groups']} decisions |")
        low = load_results(result_path(task, model, "low"))
        if low:
            s_low = summarise(items, low, slug, task)
            s_main = summaries.get(slug)
            same = [r for r in load_results(result_path(task, model)) if r["item_id"] in {x["item_id"] for x in low}]
            s_same = summarise(items, same, slug, task) if same else None
            extra.append(
                f"| {model.name} | thinking on (low) | {pct(s_low.accuracy)} on {s_low.n_items} items, against "
                f"{pct(s_same.accuracy) if s_same else '–'} with thinking off on the same items; "
                f"p50 {ms(s_low.latency_p50_ms)}; {usd(s_low.cost_per_1k_decisions, 3)} per 1k decisions |"
            )
    if extra:
        lines += ["", "## Consistency and thinking", "", "| Model | Run | Result |", "|---|---|---|"] + extra
    lines.append("")
    return "\n".join(lines), summaries


def summary_report(all_summaries: dict[str, dict[str, Summary]]) -> str:
    task_names = list(all_summaries)
    lines = [
        "# Summary",
        "",
        f"Generated {date.today().isoformat()}. Accuracy per task, majority baseline in the last row. "
        "Each task's own report has the confidence intervals, calibration, latency and cost.",
        "",
        "| Model | Kind | " + " | ".join(task_names) + " | Mean |",
        "|---|---|" + "---|" * (len(task_names) + 1),
    ]
    for slug, model in MODELS.items():
        accs = [all_summaries[t][slug].accuracy for t in task_names if slug in all_summaries[t]]
        if not accs:
            continue
        cells = [pct(all_summaries[t][slug].accuracy) if slug in all_summaries[t] else "–" for t in task_names]
        lines.append(f"| {model.name} | {model.family} | " + " | ".join(cells) + f" | {pct(sum(accs) / len(accs))} |")
    bases = [pct(majority_baseline(tasks.load(t))) for t in task_names]
    lines.append("| Majority class | baseline | " + " | ".join(bases) + " | |")
    lines += ["", "## Latency, cost and failures", "",
              "Median latency over all tasks, cost per 1,000 decisions over all tasks, and format failures in total.", "",
              "| Model | p50 | p95 | Per 1k decisions | Format failures | Decisions |", "|---|---|---|---|---|---|"]
    for slug, model in MODELS.items():
        ss = [all_summaries[t][slug] for t in task_names if slug in all_summaries[t]]
        if not ss:
            continue
        lat = sorted(x for t in task_names if slug in all_summaries[t]
                     for x in [r["latency_ms"] for r in load_results(result_path(t, model)) if r.get("latency_ms")])
        cost = sum(s.cost_usd for s in ss)
        dec = sum(s.n_decisions for s in ss)
        p50 = lat[len(lat) // 2] if lat else None
        p95 = lat[int(0.95 * (len(lat) - 1))] if lat else None
        lines.append(f"| {model.name} | {ms(p50)} | {ms(p95)} | {usd(cost / dec * 1000, 3) if dec else '–'} | "
                     f"{sum(s.format_failures for s in ss)} | {dec} |")
    if LEDGER.exists():
        total = sum(float(r["cost_usd"]) for r in csv.DictReader(LEDGER.open(encoding="utf-8")))
        lines += ["", f"Total spent across every run in `ledger.csv`: {usd(total, 2)}.", ""]
    return "\n".join(lines)


def write_all() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    all_summaries: dict[str, dict[str, Summary]] = {}
    for task in tasks.TASKS:
        text, summaries = task_report(task)
        if summaries:
            (REPORTS_DIR / f"{task}.md").write_text(text, encoding="utf-8")
            all_summaries[task] = summaries
    (REPORTS_DIR / "summary.md").write_text(summary_report(all_summaries), encoding="utf-8")
    (REPORTS_DIR / "summary.json").write_text(
        json.dumps({t: {m: s.__dict__ for m, s in ss.items()} for t, ss in all_summaries.items()}, indent=1),
        encoding="utf-8",
    )


if __name__ == "__main__":
    write_all()
