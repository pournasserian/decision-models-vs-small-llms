from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
REPORTS_DIR = ROOT / "reports"
LEDGER = ROOT / "ledger.csv"

SEED = 20261023
HARD_CAP_USD = float(os.environ.get("BENCH_CAP_USD", "100"))


@dataclass
class Model:
    slug: str  # file-safe name used in results/
    name: str  # display name
    id: str  # id at its gateway
    kind: str  # "decisions" (OpenRouter Decisions API), "chat" (OpenRouter chat), "vercel" (Vercel AI Gateway /v1/evaluate)
    family: str  # "decision model" or "LLM"
    open_weights: bool = False
    reasoning: dict | None = None  # OpenRouter reasoning block for the main run
    reasoning_low: dict | None = None  # the variant with thinking on
    temperature: float | None = 0.0
    concurrency: int = 4
    extra: dict = field(default_factory=dict)


MODELS: dict[str, Model] = {
    m.slug: m
    for m in [
        Model("jev-1.14", "Jev 1.14 (TypeSafe)", "typesafe/jev-1.14", "decisions", "decision model", temperature=None),
        Model("kev-4b", "Kev-4B", "jaredpalmer/kev-4b", "decisions", "decision model", open_weights=True, temperature=None),
        Model("laya", "Laya 421M", "convaiinnovations/laya", "vercel", "decision model", open_weights=True, temperature=None),
        # Baseten's free tier is the only endpoint: 1,000 requests a day on OpenRouter, so this one runs
        # one request at a time and over several days (the runner redoes what the limit refused)
        Model("mammoth-1", "Mammoth-1 (Baseten)", "baseten/mammoth-1:free", "decisions", "decision model",
              temperature=None, concurrency=1),
        Model(
            "haiku-5.5",
            "Claude Haiku 5.5",
            "anthropic/claude-haiku-5.5",
            "chat",
            "LLM",
            reasoning={"enabled": False},
            reasoning_low={"effort": "low"},
            temperature=None,  # Haiku 5.5 does not take temperature
        ),
        Model(
            "gemini-3.5-flash-lite",
            "Gemini 3.5 Flash Lite",
            "google/gemini-3.5-flash-lite",
            "chat",
            "LLM",
            # thinking cannot be switched off on this model; minimal is its floor
            reasoning={"effort": "minimal"},
            reasoning_low={"effort": "low"},
        ),
        Model(
            "gpt-5.4-nano",
            "GPT-5.4 nano",
            "openai/gpt-5.4-nano",
            "chat",
            "LLM",
            reasoning={"effort": "none"},
            reasoning_low={"effort": "low"},
            temperature=None,  # the GPT-5 family rejects temperature
        ),
        Model(
            "qwen3.6-35b-a3b",
            "Qwen3.6 35B-A3B",
            "qwen/qwen3.6-35b-a3b",
            "chat",
            "LLM",
            open_weights=True,
            reasoning={"enabled": False},
            reasoning_low={"effort": "low"},
        ),
        Model(
            "gemma-4-26b-a4b",
            "Gemma 4 26B-A4B",
            "google/gemma-4-26b-a4b-it",
            "chat",
            "LLM",
            open_weights=True,
            reasoning={"enabled": False},
            reasoning_low={"effort": "low"},
        ),
    ]
}

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
VERCEL_KEY = os.environ.get("AI_GATEWAY_API_KEY", "")
