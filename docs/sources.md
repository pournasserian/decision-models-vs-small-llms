# Sources outside this repository

Facts about the models and the field that the article draws on, each with where it was read and when.
Everything else the article says comes from `reports/`, `results/`, `ledger.csv` and `README.md`.

## Jev (TypeSafe AI)

- Early access since mid-September 2026; the first of TypeSafe's "System One" models; input tokens are billed and output tokens are free. OpenRouter lists 1.13 and 1.14 and the alias `~typesafe/jev-latest`; 1.14 is the current release and the one run here (`typesafe/jev-1.14-20261014` in responses). Read 2026-10-23 at https://openrouter.ai/typesafe and https://openrouter.ai/docs/guides/community/jev.
- The Decisions API: `POST https://openrouter.ai/api/alpha/decisions`, a `state` and named `questions` of type `choice` (options as `criteria` keys), `score` (ordered levels) or `noul` (yes/no); each answer carries probabilities and, for choice and score, a confidence; `usage.cost` in dollars. Read 2026-10-23 at https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-questions-and-answers-request.md.
- Context 262,144 tokens; requests over about 32,000 bytes of text run in a slower long-context mode; image input and a `box` primitive are early features in 1.14. Same guide.
- Published price: $0.042 per million input tokens, output free (Cloudflare's model page, read 2026-10-23, https://developers.cloudflare.com/ai/models/typesafe/jev/). The measured cost in `ledger.csv` is what OpenRouter charged.
- On the typed-decisions leaderboard, Jev 1.13.0 scores 0.727 accuracy, KL from gold 1.442, Brier 0.148, ECE 0.144, p50 710 ms (dataset card, read 2026-10-23).

## Kev (Jared Palmer)

- "Jev-like family of decision models built on top of Qwen3.5/3.8 you can train and run on your own", Apache 2.0, four sizes (0.8B, 4B, 9B, 27B) versioned as Kev 1.0; its server speaks TypeSafe's API, so TypeSafe's SDK clients can point at it. Kev-4B is the recommended starting checkpoint. Repository https://github.com/jaredpalmer/kev, read 2026-10-23 (about 9,500 stars, last push that day).
- Validated context 8,192 tokens for 0.8B, 4B and 9B. Speed on an H100: six questions about a short text in 18.1 ms of model time. Same README.
- On OpenRouter as `jaredpalmer/kev-4b` (`jaredpalmer/kev-4b-20260924` in responses), served by Phala; input and output tokens both billed.

## Laya (ConvAI Innovations)

- A non-autoregressive decision model: ModernBERT-large encoder with a decision head, 421M parameters, 512-token context, Apache 2.0, released on Hugging Face in September 2026. Each option is scored at its own mask token and softmaxed across the question's options. Model card https://huggingface.co/convaiinnovations/laya, read 2026-10-23.
- The card's own zero-shot figures: MASSIVE intent (English) 0.783; XNLI (English) 0.860; AG News 0.950 against Jev's published 0.910; DAIR Emotion 0.595 against 0.480; Banking77 0.425 against Jev's 0.870 (the card notes accuracy drops with many options). On typed-decisions the base checkpoints score 0.34 to 0.36, below the 0.461 majority baseline; the fine-tuned `laya-typed-decisions` checkpoint 0.766.
- The card says it is "not a zero-shot decision engine" and recommends fine-tuning and calibrating on your own data; the models ship overconfident; the root checkpoint is English only.
- Speed on a Tesla T4: 39.5 ms for one question, 158.6 ms for ten batched; on CPU 193 to 464 ms.
- Hosted on Vercel AI Gateway as `convaiinnovations/laya`, free through 31 October 2026 (Vercel changelog, read 2026-10-23); not on OpenRouter.

## Mammoth-1 (Baseten)

- "A 27B decision model from Base Labs, Baseten's research team, built on Qwen3.5-27B", text or JSON state and typed questions. On OpenRouter as `baseten/mammoth-1:free` only (`baseten/mammoth-1-20261021` in responses), the free tier, which OpenRouter limits to 1,000 requests a day for an account with a high balance (`free-models-per-day-high-balance`, seen 2026-10-24). Model page https://openrouter.ai/baseten/mammoth-1, read 2026-10-23.
- On the typed-decisions leaderboard: 0.768 accuracy, KL 0.122, Brier 0.063, ECE 0.153, p50 415 ms, third among zero-shot models.

## The typed-decisions benchmark

- https://huggingface.co/datasets/LocalLLaMA/typed-decisions, Apache 2.0. Test split: 400 cases, five typed questions each, 2,000 decisions, four synthetic workflows (agent-trace observability, customer service, invoice processing, security incidents); the gold is a probability distribution per question. Independent of TypeSafe. Read 2026-10-23.
- Its leaderboard that day listed 38 zero-shot decision models, from Quyet-1.0-Large (0.791) and meraGPT Decider 1 (0.768, the lowest KL and Brier) down, with Jev 1.13 at 0.727 in 17th place, and 27 more models fitted or fine-tuned on the train split, which it keeps in a separate table. Reference rows: prior that ignores the input 0.470, uniform 0.308.

## The LLMs

OpenRouter catalogue, read 2026-10-23; prices per million tokens, input and output, at the endpoint OpenRouter routed to.

| Model | Id | Released on OpenRouter | List price in / out |
|---|---|---|---|
| Claude Haiku 5.5 | `anthropic/claude-haiku-5.5` | 2026-10-07 | $0.10 / $0.50 |
| Gemini 3.5 Flash Lite | `google/gemini-3.5-flash-lite` | 2026-07-21 | $0.15 to $0.30 / $1.25 to $2.50 |
| GPT-5.4 nano | `openai/gpt-5.4-nano` | 2026-03-17 | $0.10 to $0.20 / $0.625 to $1.25 |
| Qwen3.6 35B-A3B | `qwen/qwen3.6-35b-a3b` | 2026-04-26 | $0.05 to $0.10 / $0.70 to $1.00 |
| Gemma 4 26B-A4B | `google/gemma-4-26b-a4b-it` | 2026-04-03 | $0.04 to $0.09 / $0.22 to $0.34 |

- Gemini 3.5 Flash Lite cannot switch thinking off; `minimal` is its floor. Claude Haiku 5.5 and GPT-5.4 nano do not accept a temperature. Anthropic's endpoint rejects a strict JSON schema with 77 numeric fields as too large a grammar.

## Datasets

- Banking77: PolyAI, CC BY 4.0, 77 intents, test split 3,080; `legacy-datasets/banking77` on the Hub.
- CLINC150: CC BY 3.0, 150 intents in 10 domains plus out of scope, `plus` test split 5,500 (1,000 out of scope); the domain mapping is `data/domains.json` in https://github.com/clinc/oos-eval.
- deepset/prompt-injections: Apache 2.0, 546 train and 116 test, English and German.
- SST-5: `SetFit/sst5`, test 2,210, five levels.
- AG News: `fancyzhx/ag_news`, test 7,600, four classes; licence listed as unknown on the Hub.
