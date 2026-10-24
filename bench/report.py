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
        "| Model | Kind | Items | Accuracy | 95% CI | Brier (top-1) | ECE | Format failures | p50 | p95 | Cost | Per 1k decisions |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in rows:
        m = MODELS[s.model]
        lines.append(
            f"| {m.name} | {m.family} | {s.n_items} | {pct(s.accuracy)} | {pct(s.ci_low)} to {pct(s.ci_high)} | {num(s.brier)} | "
            f"{num(s.ece)} | {s.format_failures} | {ms(s.latency_p50_ms)} | {ms(s.latency_p95_ms)} | "
            f"{usd(s.cost_usd)} | {usd(s.cost_per_1k_decisions, 3)} |"
        )
    lines.append(f"| Majority class | baseline | | {pct(base)} | | | | | | | | |")
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
                  "KL divergence from the benchmark's gold distribution, for the decision models, which return one; an LLM here reports a confidence, not a distribution.", "",
                  "| Model | KL from gold |", "|---|---|"]
        for s in rows:
            if s.kl_from_gold is not None and MODELS[s.model].family == "decision model":
                lines.append(f"| {MODELS[s.model].name} | {num(s.kl_from_gold)} |")
    lines += task_specific(task, items, {slug: load_results(result_path(task, MODELS[slug])) for slug in summaries})
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


def _label(r: dict, q: str) -> str | None:
    return ((r.get("answers") or {}).get(q) or {}).get("label")


def task_specific(task: str, items: list, results: dict[str, list[dict]]) -> list[str]:
    """Extra tables one task calls for: out-of-scope handling, level distance, per-workflow accuracy."""
    by_id = {it.id: it for it in items}
    out: list[str] = []
    if task == "clinc-domains":
        n_oos = sum(it.gold["domain"] == "out of scope" for it in items)
        out += ["", "## Out of scope", "", f"{n_oos} of the {len(items)} requests are out of scope. How often each model "
                "said so, how many of the true ones it caught, and its accuracy on the in-scope requests alone.", "",
                "| Model | Said out of scope | Caught | In-scope accuracy |", "|---|---|---|---|"]
        for slug, rs in results.items():
            main = [r for r in rs if r.get("repeat", 0) == 0 and r["item_id"] in by_id]
            said = sum(_label(r, "domain") == "out of scope" for r in main)
            caught = sum(_label(r, "domain") == "out of scope" for r in main if by_id[r["item_id"]].gold["domain"] == "out of scope")
            ins = [_label(r, "domain") == by_id[r["item_id"]].gold["domain"] for r in main if by_id[r["item_id"]].gold["domain"] != "out of scope"]
            out.append(f"| {MODELS[slug].name} | {said} | {caught} of {n_oos} | {pct(sum(ins) / len(ins)) if ins else '–'} |")
    elif task == "sst5":
        out += ["", "## Distance from the gold level", "", "Mean absolute distance between the chosen level and the gold "
                "level (0 to 4), and the share of answers within one level.", "",
                "| Model | Mean distance | Within one level |", "|---|---|---|"]
        for slug, rs in results.items():
            d = [abs(int(_label(r, "sentiment")) - int(by_id[r["item_id"]].gold["sentiment"]))
                 for r in rs if r.get("repeat", 0) == 0 and r["item_id"] in by_id and _label(r, "sentiment") is not None]
            if d:
                out.append(f"| {MODELS[slug].name} | {sum(d) / len(d):.3f} | {pct(sum(x <= 1 for x in d) / len(d))} |")
    elif task == "typed-decisions":
        wfs = sorted({it.id.rsplit("_", 1)[0] for it in items})
        out += ["", "## By workflow", "", "| Model | " + " | ".join(w.replace("_", " ") for w in wfs) + " |",
                "|---|" + "---|" * len(wfs)]
        for slug, rs in results.items():
            acc = {w: [0, 0] for w in wfs}
            for r in rs:
                if r.get("repeat", 0) or r["item_id"] not in by_id:
                    continue
                w = r["item_id"].rsplit("_", 1)[0]
                for q, g in by_id[r["item_id"]].gold.items():
                    acc[w][1] += 1
                    acc[w][0] += _label(r, q) == g
            out.append(f"| {MODELS[slug].name} | " + " | ".join(pct(c / n) if n else "–" for c, n in acc.values()) + " |")
    return out


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
