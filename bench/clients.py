"""One client per gateway. Each returns a Result for one item; the runner handles concurrency and retries."""

from __future__ import annotations

import json
import time
from typing import Any

import httpx

from .config import OPENROUTER_KEY, VERCEL_KEY, Model
from .llm_prompt import SYSTEM, json_schema, max_tokens, parse, user_message
from .schema import Answer, Item, Question, Result

OPENROUTER_DECISIONS = "https://openrouter.ai/api/alpha/decisions"
OPENROUTER_CHAT = "https://openrouter.ai/api/v1/chat/completions"
VERCEL_EVALUATE = "https://ai-gateway.vercel.sh/v1/evaluate"

HEADERS_OR = {
    "Authorization": f"Bearer {OPENROUTER_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/pournasserian/decision-models-vs-small-llms",
    "X-Title": "decision-models-vs-small-llms",
}


class RetryableError(Exception):
    pass


def _check(r: httpx.Response) -> dict:
    if r.status_code in (408, 429, 500, 502, 503, 504, 524, 529):
        raise RetryableError(f"{r.status_code}: {r.text[:300]}")
    if r.status_code >= 400:
        raise httpx.HTTPStatusError(f"{r.status_code}: {r.text[:500]}", request=r.request, response=r)
    return r.json()


def decision_answers(item: Item, answers_raw: dict, boolean_key: str = "noul") -> tuple[dict[str, Answer], str | None]:
    """Normalise a System One style answer block into our Answer shape."""
    answers: dict[str, Answer] = {}
    errors = []
    for name, q in item.questions.items():
        a = answers_raw.get(name)
        if not isinstance(a, dict):
            errors.append(f"{name}: missing")
            continue
        opts = q.options()
        if q.type == "noul":
            p = a.get(boolean_key, a.get("probability"))
            if p is None:
                errors.append(f"{name}: no probability")
                continue
            p = float(p)
            answers[name] = Answer("true" if p >= 0.5 else "false", {"true": p, "false": 1 - p}, max(p, 1 - p))
            continue
        probs_raw = a.get("probabilities") or {}
        probs = {o: float(probs_raw.get(o, 0.0)) for o in opts}
        if q.type == "choice":
            label = a.get("choice")
            if label is None:
                label = max(probs, key=probs.get) if any(probs.values()) else None
        else:
            # a score answer carries an interpolated value; the label is the most probable rung
            label = max(probs, key=probs.get) if any(probs.values()) else None
        if label not in opts:
            errors.append(f"{name}: '{label}' is not an option")
            continue
        conf = a.get("confidence")
        answers[name] = Answer(str(label), probs, float(conf) if conf is not None else max(probs.values()))
    return answers, ("; ".join(errors) if errors else None)


def wire_questions(item: Item) -> dict[str, Any]:
    return {n: q.to_wire() for n, q in item.questions.items()}


async def call_openrouter_decisions(client: httpx.AsyncClient, model: Model, item: Item, task: str, **meta) -> Result:
    body = {"model": model.id, "state": item.state, "questions": wire_questions(item)}
    t0 = time.perf_counter()
    r = await client.post(OPENROUTER_DECISIONS, headers=HEADERS_OR, json=body, timeout=120)
    latency = (time.perf_counter() - t0) * 1000
    data = _check(r)
    answers, err = decision_answers(item, data.get("answers", {}))
    usage = data.get("usage", {})
    return Result(
        item.id, model.slug, task, answers, latency, usage.get("cost"), usage.get("input_tokens"),
        usage.get("output_tokens"), err, data, body, **meta,
    )


async def call_vercel_decisions(client: httpx.AsyncClient, model: Model, item: Item, task: str, **meta) -> Result:
    # Vercel's native shape calls noul "boolean"; everything else is TypeSafe's shape
    questions = {}
    for n, q in item.questions.items():
        w = q.to_wire()
        if q.type == "noul":
            w["type"] = "boolean"
        questions[n] = w
    body = {"model": model.id, "state": item.state, "questions": questions}
    if model.extra.get("only"):
        body["providerOptions"] = {"gateway": {"only": model.extra["only"]}}
    headers = {"Authorization": f"Bearer {VERCEL_KEY}", "Content-Type": "application/json"}
    t0 = time.perf_counter()
    r = await client.post(VERCEL_EVALUATE, headers=headers, json=body, timeout=120)
    latency = (time.perf_counter() - t0) * 1000
    data = _check(r)
    answers, err = decision_answers(item, data.get("answers", {}), boolean_key="probability")
    usage = data.get("usage", {})
    cost = ((data.get("providerMetadata") or {}).get("gateway") or {}).get("cost")
    return Result(
        item.id, model.slug, task, answers, latency, float(cost) if cost is not None else None,
        usage.get("inputTokens"), usage.get("outputTokens"), err, data, body, **meta,
    )


async def call_openrouter_chat(
    client: httpx.AsyncClient, model: Model, item: Item, task: str, reasoning: dict | None = None, **meta
) -> Result:
    body: dict[str, Any] = {
        "model": model.id,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_message(item)}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "answers", "strict": True, "schema": json_schema(item)},
        },
        "provider": {"require_parameters": True},
        "usage": {"include": True},
        "max_tokens": max_tokens(item),
    }
    if model.temperature is not None:
        body["temperature"] = model.temperature
    rsn = reasoning if reasoning is not None else model.reasoning
    if rsn:
        body["reasoning"] = rsn
    if reasoning is not None:
        # thinking on: the budget must hold the thinking too, or the answer is cut off before it starts
        body["max_tokens"] = 8000
    t0 = time.perf_counter()
    r = await client.post(OPENROUTER_CHAT, headers=HEADERS_OR, json=body, timeout=180)
    latency = (time.perf_counter() - t0) * 1000
    data = _check(r)
    if "error" in data and not data.get("choices"):
        raise RetryableError(json.dumps(data["error"])[:300])
    choice = data["choices"][0]
    text = choice["message"].get("content") or ""
    answers, err = parse(item, text)
    if choice.get("finish_reason") == "length" and err:
        err = "truncated: " + err
    usage = data.get("usage", {})
    return Result(
        item.id, model.slug, task, answers, latency, usage.get("cost"), usage.get("prompt_tokens"),
        usage.get("completion_tokens"), err, data, body, **meta,
    )


async def call(client: httpx.AsyncClient, model: Model, item: Item, task: str, **meta) -> Result:
    if model.kind == "decisions":
        return await call_openrouter_decisions(client, model, item, task, **meta)
    if model.kind == "vercel":
        return await call_vercel_decisions(client, model, item, task, **meta)
    return await call_openrouter_chat(client, model, item, task, **meta)
