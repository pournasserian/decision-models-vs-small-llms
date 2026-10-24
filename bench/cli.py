from __future__ import annotations

import argparse
import asyncio
import json
import sys

from . import tasks
from .config import MODELS, VERCEL_KEY, Model
from .metrics import majority_baseline, summarise
from .runner import load_results, result_path, run, spent


def pick_models(names: list[str] | None) -> list[Model]:
    if not names or names == ["all"]:
        return list(MODELS.values())
    return [MODELS[n] for n in names]


def pick_tasks(names: list[str] | None) -> list[str]:
    if not names or names == ["all"]:
        return list(tasks.TASKS)
    return names


def cmd_run(args: argparse.Namespace) -> None:
    for task in pick_tasks(args.task):
        items = tasks.load(task, args.n)
        for model in pick_models(args.model):
            variant = args.variant
            reasoning = None
            if variant == "low":
                if model.kind != "chat":
                    continue
                reasoning = model.reasoning_low
            if model.kind == "vercel" and not VERCEL_KEY:
                print(f"skip {model.slug}: AI_GATEWAY_API_KEY not set", file=sys.stderr)
                continue
            results = asyncio.run(
                run(task, model, items, variant=variant, reasoning=reasoning, repeats=args.repeats, limit=args.limit)
            )
            s = summarise(items, results, model.slug, task)
            print(
                f"{task:18} {model.slug:24} acc {s.accuracy:.3f} [{s.ci_low:.3f},{s.ci_high:.3f}] "
                f"n={s.n_decisions} fail={s.format_failures} p50={s.latency_p50_ms and round(s.latency_p50_ms)}ms "
                f"${s.cost_usd:.4f} base={majority_baseline(items):.3f}"
            )
    print(f"total spent so far: ${spent():.4f}", file=sys.stderr)


def cmd_show(args: argparse.Namespace) -> None:
    task = args.task
    items = tasks.load(task, args.n)
    model = MODELS[args.model]
    results = load_results(result_path(task, model, args.variant))
    by_id = {it.id: it for it in items}
    shown = 0
    for r in results:
        it = by_id.get(r["item_id"])
        if not it:
            continue
        wrong = [q for q in it.questions if ((r.get("answers") or {}).get(q) or {}).get("label") != it.gold[q]]
        if args.wrong and not wrong and not r.get("format_error"):
            continue
        state = it.state if isinstance(it.state, str) else json.dumps(it.state)[:200]
        print(f"--- {r['item_id']}  err={r.get('format_error')}  {state[:160]!r}")
        for q in it.questions:
            a = (r.get("answers") or {}).get(q) or {}
            print(f"    {q}: gold={it.gold[q]!r} got={a.get('label')!r} conf={a.get('confidence')}")
        shown += 1
        if shown >= args.limit:
            break


def main() -> None:
    p = argparse.ArgumentParser(prog="bench")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run models over tasks (resumable)")
    r.add_argument("--task", nargs="*", help="task names, or all")
    r.add_argument("--model", nargs="*", help="model slugs, or all")
    r.add_argument("--n", type=int, help="items per task (default: the task's default)")
    r.add_argument("--limit", type=int, help="at most this many new requests per model and task")
    r.add_argument("--variant", default="main", choices=["main", "low"])
    r.add_argument("--repeats", type=int, default=1)
    r.set_defaults(func=cmd_run)
    s = sub.add_parser("show", help="print items with their gold and predicted labels")
    s.add_argument("task")
    s.add_argument("model")
    s.add_argument("--n", type=int)
    s.add_argument("--variant", default="main")
    s.add_argument("--wrong", action="store_true")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(func=cmd_show)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
