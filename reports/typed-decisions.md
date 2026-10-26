# typed-decisions

Agent-trace, support, invoice and security decisions, five mixed questions per case.

Data: LocalLLaMA/typed-decisions test split, Apache 2.0. 400 items, 2000 decisions. Majority-class baseline: 46.1%.

| Model | Kind | Items | Accuracy | 95% CI | Brier (top-1) | ECE | Format failures | p50 | p95 | Cost | Per 1k decisions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev 1.14 (TypeSafe) | decision model | 400 | 74.6% | 72.6% to 76.5% | 0.173 | 0.057 | 0 | 143 ms | 203 ms | $0.0159 | $0.008 |
| Gemma 4 26B-A4B | LLM | 400 | 74.6% | 72.6% to 76.4% | 0.208 | 0.171 | 0 | 1,784 ms | 4,303 ms | $0.0373 | $0.019 |
| Claude Haiku 5.5 | LLM | 400 | 72.7% | 70.7% to 74.6% | 0.178 | 0.030 | 0 | 1,316 ms | 1,635 ms | $0.0916 | $0.046 |
| Gemini 3.5 Flash Lite | LLM | 400 | 71.5% | 69.5% to 73.4% | 0.232 | 0.194 | 0 | 820 ms | 978 ms | $0.2137 | $0.107 |
| Qwen3.6 35B-A3B | LLM | 400 | 67.4% | 65.3% to 69.4% | 0.241 | 0.188 | 7 | 1,856 ms | 4,653 ms | $0.0926 | $0.046 |
| Kev-4B | decision model | 400 | 66.8% | 64.8% to 68.9% | 0.242 | 0.173 | 0 | 367 ms | 583 ms | $0.0085 | $0.004 |
| GPT-5.4 nano | LLM | 400 | 66.8% | 64.7% to 68.8% | 0.214 | 0.075 | 0 | 977 ms | 1,362 ms | $0.0974 | $0.049 |
| Laya 421M | decision model | 400 | 35.4% | 33.4% to 37.6% | 0.258 | 0.157 | 7 | 406 ms | 1,125 ms | $0.0000 | $0.000 |
| Majority class | baseline | | 46.1% | | | | | | | | |

## By question type

| Model | choice | noul | score |
|---|---|---|---|
| Jev 1.14 (TypeSafe) | 71.0% (600) | 82.3% (600) | 71.5% (800) |
| Gemma 4 26B-A4B | 72.5% (600) | 81.0% (600) | 71.2% (800) |
| Claude Haiku 5.5 | 66.3% (600) | 81.5% (600) | 70.8% (800) |
| Gemini 3.5 Flash Lite | 68.7% (600) | 83.0% (600) | 65.0% (800) |
| Qwen3.6 35B-A3B | 66.3% (600) | 78.7% (600) | 59.8% (800) |
| Kev-4B | 64.7% (600) | 76.2% (600) | 61.5% (800) |
| GPT-5.4 nano | 66.5% (600) | 78.5% (600) | 58.2% (800) |
| Laya 421M | 28.5% (600) | 47.5% (600) | 31.6% (800) |

## Against the soft gold

KL divergence from the benchmark's gold distribution, for the decision models, which return one; an LLM here reports a confidence, not a distribution.

| Model | KL from gold |
|---|---|
| Jev 1.14 (TypeSafe) | 0.824 |
| Kev-4B | 0.225 |
| Laya 421M | 0.564 |

## By workflow

| Model | agent trace observability | customer service | invoice processing | security incidents |
|---|---|---|---|---|
| Jev 1.14 (TypeSafe) | 62.8% | 83.4% | 79.0% | 73.2% |
| Kev-4B | 57.0% | 72.2% | 68.2% | 70.0% |
| Laya 421M | 38.8% | 36.2% | 35.2% | 31.6% |
| Claude Haiku 5.5 | 64.0% | 80.0% | 75.4% | 71.2% |
| Gemini 3.5 Flash Lite | 62.2% | 76.6% | 77.4% | 69.8% |
| GPT-5.4 nano | 57.4% | 76.0% | 67.0% | 66.8% |
| Qwen3.6 35B-A3B | 62.2% | 72.8% | 70.4% | 64.2% |
| Gemma 4 26B-A4B | 68.8% | 80.6% | 76.2% | 72.6% |

## Consistency and thinking

| Model | Run | Result |
|---|---|---|
| Jev 1.14 (TypeSafe) | repeats | 98.2% over 500 decisions |
| Kev-4B | repeats | 99.0% over 500 decisions |
| Claude Haiku 5.5 | repeats | 91.2% over 500 decisions |
| Claude Haiku 5.5 | thinking on (low) | 61.2% on 100 items, against 64.0% with thinking off on the same items; p50 1,380 ms; $0.042 per 1k decisions |
| Gemini 3.5 Flash Lite | repeats | 90.0% over 500 decisions |
| Gemini 3.5 Flash Lite | thinking on (low) | 60.8% on 100 items, against 62.2% with thinking off on the same items; p50 812 ms; $0.093 per 1k decisions |
| GPT-5.4 nano | repeats | 76.8% over 500 decisions |
| GPT-5.4 nano | thinking on (low) | 57.2% on 100 items, against 57.4% with thinking off on the same items; p50 2,118 ms; $0.070 per 1k decisions |
| Qwen3.6 35B-A3B | repeats | 86.8% over 500 decisions |
| Qwen3.6 35B-A3B | thinking on (low) | 66.8% on 100 items, against 62.2% with thinking off on the same items; p50 24,453 ms; $0.560 per 1k decisions |
| Gemma 4 26B-A4B | repeats | 80.6% over 500 decisions |
| Gemma 4 26B-A4B | thinking on (low) | 69.4% on 100 items, against 68.8% with thinking off on the same items; p50 27,799 ms; $0.160 per 1k decisions |
