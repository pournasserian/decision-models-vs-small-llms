from __future__ import annotations

from collections.abc import Callable

from ..schema import Item
from . import ag_news, banking77, clinc_domains, prompt_injection, sst5, typed_decisions

# name -> (loader(n) -> items, default n, one-line description, dataset citation)
TASKS: dict[str, tuple[Callable[[int | None], list[Item]], int | None, str, str]] = {
    "banking77": (
        banking77.load,
        1000,
        "Intent routing with 77 options (choice)",
        "Banking77, PolyAI, CC BY 4.0, test split",
    ),
    "clinc-domains": (
        clinc_domains.load,
        1000,
        "Routing to 10 domains plus out of scope (choice)",
        "CLINC150 'plus' test split, CC BY 3.0, domains from clinc/oos-eval",
    ),
    "prompt-injection": (
        prompt_injection.load,
        None,
        "Is this text a prompt injection? (noul)",
        "deepset/prompt-injections, Apache 2.0, train and test splits",
    ),
    "sst5": (
        sst5.load,
        1000,
        "Sentiment on five ordered levels (score)",
        "SST-5 test split, SetFit/sst5",
    ),
    "ag-news": (
        ag_news.load,
        1000,
        "News topic, four options (choice)",
        "AG News test split, fancyzhx/ag_news",
    ),
    "typed-decisions": (
        typed_decisions.load,
        None,
        "Agent-trace, support, invoice and security decisions, five mixed questions per case",
        "LocalLLaMA/typed-decisions test split, Apache 2.0",
    ),
}


def load(name: str, n: int | None = None) -> list[Item]:
    loader, default_n, _, _ = TASKS[name]
    return loader(default_n if n is None else n)
