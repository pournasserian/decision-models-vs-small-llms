# Decision models against small LLMs

A rerunnable comparison of the new "decision models" (Jev, Kev, Laya, Mammoth-1) with small, cheap LLMs
(Claude Haiku 5.5, Gemini 3.5 Flash Lite, GPT-5.4 nano, Qwen3.6 35B-A3B, Gemma 4 26B-A4B) on six
decisions an agent makes between its generative steps: routing, classification, a guardrail,
an ordered score and a mixed workflow benchmark.

Every model gets the same question in TypeSafe's System One shape (a `choice`, a `score` or a yes/no `noul`,
each with its `instructions` and `criteria`). Decision models take it as is. LLMs get it rendered as a prompt
and answer under a strict JSON schema. The raw request and response of every call is in `results/`, the
spending in `ledger.csv`, and the tables in `reports/`.

The results are discussed in an article on [pournasserian.com](https://pournasserian.com/writing).

## Models

| Slug | Model | Kind | Gateway | Version seen in responses |
|---|---|---|---|---|
| `jev-1.14` | Jev 1.14, TypeSafe AI | decision model, proprietary | OpenRouter Decisions API | `typesafe/jev-1.14-20261014` |
| `kev-4b` | Kev-4B, Jared Palmer | decision model, Apache 2.0, from Qwen3.5-4B | OpenRouter Decisions API | `jaredpalmer/kev-4b-20260924` |
| `laya` | Laya 421M, ConvAI Innovations | decision model, Apache 2.0, ModernBERT encoder, zero-shot | Vercel AI Gateway `/v1/evaluate` | |
| `mammoth-1` | Mammoth-1, Baseten (Base Labs) | decision model, 27B from Qwen3.5-27B, free tier | OpenRouter Decisions API | `baseten/mammoth-1-20261021` |
| `haiku-5.5` | Claude Haiku 5.5 | LLM | OpenRouter chat | `claude-haiku-5.5-20261007` |
| `gemini-3.5-flash-lite` | Gemini 3.5 Flash Lite | LLM | OpenRouter chat | `gemini-3.5-flash-lite-20260721` |
| `gpt-5.4-nano` | GPT-5.4 nano | LLM | OpenRouter chat | `gpt-5.4-nano-20260317` |
| `qwen3.6-35b-a3b` | Qwen3.6 35B-A3B | LLM, open weights | OpenRouter chat | `qwen3.6-35b-a3b` (2026-04-26) |
| `gemma-4-26b-a4b` | Gemma 4 26B-A4B | LLM, open weights | OpenRouter chat | `gemma-4-26b-a4b-it-20260403` |

Adding a model is one line in `bench/config.py`.

## Tasks

| Task | Decision | Data | Items |
|---|---|---|---|
| `banking77` | intent routing, 77 options (`choice`) | Banking77 test split, PolyAI, CC BY 4.0 | 1,000 sampled |
| `clinc-domains` | routing to 10 domains plus "out of scope" (`choice`) | CLINC150 `plus` test split, CC BY 3.0, domains from [clinc/oos-eval](https://github.com/clinc/oos-eval) | 1,000 sampled |
| `prompt-injection` | is this a prompt injection? (`noul`) | [deepset/prompt-injections](https://huggingface.co/datasets/deepset/prompt-injections), Apache 2.0, both splits | 662, all |
| `sst5` | sentiment on five ordered levels (`score`) | SST-5 test split, [SetFit/sst5](https://huggingface.co/datasets/SetFit/sst5) | 1,000 sampled |
| `ag-news` | news section, four options (`choice`) | AG News test split, [fancyzhx/ag_news](https://huggingface.co/datasets/fancyzhx/ag_news) | 1,000 sampled |
| `typed-decisions` | four agent workflows, five mixed questions per case | [LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions) test split, Apache 2.0 | 400 cases, 2,000 decisions |

Samples are drawn with a fixed seed (`bench/data.py`), so a rerun scores the same items. The question
text, options and criteria of every task are in `bench/tasks/`; they are the only "prompt engineering"
there is, and every model gets the same words.

## Running it

```bash
uv sync
export OPENROUTER_API_KEY=...      # Jev, Kev and the LLMs
export AI_GATEWAY_API_KEY=...      # Laya (optional; the run skips it without a key)
export BENCH_CAP_USD=10            # the run stops when the ledger reaches this (default 100)

uv run python -m bench.cli run --task all --model all            # the main run, resumable
uv run python -m bench.cli run --task all --model all --variant repeats --subset 100 --repeats 3
uv run python -m bench.cli run --task all --model all --variant low --subset 100
uv run python -m bench.cli report                                  # writes reports/
PYTHONPATH=. uv run python scripts/strip_refused.py   # drop rate-limited rows before a rerun
uv run python -m bench.cli show banking77 jev-1.14 --wrong         # look at mistakes
```

A run appends one JSON line per request to `results/<task>/<model>.jsonl` and skips what is already there,
so it can be stopped and resumed. The ledger adds a row per run with its measured cost.

## Method

- **One question shape for everyone.** Decision models get the System One request unchanged. LLMs get a
  system prompt and the state and questions rendered as text (`bench/llm_prompt.py`), and must answer under a
  strict JSON schema (`response_format: json_schema`, `strict: true`, routed only to endpoints that support
  it) with, per question, the answer and a confidence from 0 to 100.
- **Why a confidence and not a distribution.** The first version asked LLMs for a probability per option.
  Anthropic's endpoint rejected the 77-option schema ("the compiled grammar is too large"), and Qwen and Gemma
  under the strict grammar looped on the digits of a decimal until they hit the token limit. Asking for the pick
  and a whole-number confidence fixed both and is what the metrics need.
- **Thinking off.** The main run turns reasoning off where the model allows it (Haiku, GPT-5.4 nano, Qwen,
  Gemma) and uses the lowest effort where it does not (Gemini 3.5 Flash Lite's `minimal`). The `low` variant
  reruns a subset with `effort: low` to show what thinking buys. Temperature is 0 where the model accepts it
  (Haiku 5.5 and GPT-5.4 nano do not).
- **Accuracy** is the share of decisions whose answer matches the gold label, with a Wilson 95% interval.
  A score question is scored on its most probable level. A format failure (invalid JSON, an answer outside
  the options, a truncated reply, an HTTP error after retries) counts as wrong and is also counted separately.
- **Calibration.** Brier score on the top answer, `(confidence - correct)^2`, averaged; and expected
  calibration error over ten confidence bins. For a decision model the confidence is the probability of its
  chosen option; for an LLM it is the confidence it reported. On `typed-decisions`, which has a gold
  distribution, the KL divergence from it is reported for the models that return a distribution.
- **Latency** is wall time of the HTTP call from a home connection in Toronto through the gateway, four
  requests in flight per model, p50 and p95. It includes the gateway hop for every model alike.
- **Cost** is what the gateway reported for each call (`usage.cost`), summed, and divided per 1,000 decisions.
- **Retries.** A 429, 5xx or network error is retried up to five times with backoff; a 4xx is recorded as a
  failure and not retried. A request the gateway still refused after the retries is not a measurement:
  it is dropped and redone on the next run (`scripts/strip_refused.py`, and the runner does the same on resume).
- **Format failures are kept.** When Qwen3.6 answers under the strict grammar it sometimes emits only
  whitespace until the token limit (seen on four providers, 40 of 1,000 Banking77 items). That is what a
  caller would get, so it stays in the results as a failure and is not retried.
- **Mammoth-1** is served only on OpenRouter's free tier, 1,000 requests a day, so its run is spread over
  several days at one request at a time.
- **Baselines.** Each report shows the majority-class baseline, always answering each question's most common
  gold label.

## What this does not show

- Laya is scored zero-shot with its root checkpoint, as downloaded. Its own card says it is meant to be
  fine-tuned and calibrated on your data first. We did not fine-tune anything.
- The LLM prompts are plain and the same for every model. A prompt tuned for one model would move its number.
- `prompt-injection` mixes English and German; Laya's root checkpoint is English only.
- AG News's licence is listed as unknown on the Hub; it is used here as it is used in the literature.
- One run, one week in October 2026. Every model here is a moving target.

## Layout

```
bench/            the harness (tasks, clients, runner, metrics, report)
results/          one JSONL per task and model: request, response, answers, latency, cost
reports/          Markdown tables generated from results/
ledger.csv        every run and what it cost
```

MIT licence. Dataset licences are the datasets' own, listed above.
