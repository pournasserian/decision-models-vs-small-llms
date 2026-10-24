# sst5

Sentiment on five ordered levels (score).

Data: SST-5 test split, SetFit/sst5. 1000 items, 1000 decisions. Majority-class baseline: 27.1%.

| Model | Kind | Items | Accuracy | 95% CI | Brier (top-1) | ECE | Format failures | p50 | p95 | Cost | Per 1k decisions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3.6 35B-A3B | LLM | 1000 | 59.0% | 55.9% to 62.0% | 0.331 | 0.303 | 2 | 646 ms | 2,025 ms | $0.0546 | $0.055 |
| Claude Haiku 5.5 | LLM | 1000 | 58.7% | 55.6% to 61.7% | 0.295 | 0.232 | 0 | 1,108 ms | 1,375 ms | $0.0617 | $0.062 |
| Kev-4B | decision model | 1000 | 58.6% | 55.5% to 61.6% | 0.297 | 0.215 | 0 | 329 ms | 455 ms | $0.0022 | $0.002 |
| Jev 1.14 (TypeSafe) | decision model | 1000 | 58.1% | 55.0% to 61.1% | 0.265 | 0.173 | 0 | 138 ms | 214 ms | $0.0142 | $0.014 |
| Gemma 4 26B-A4B | LLM | 1000 | 57.0% | 53.9% to 60.0% | 0.374 | 0.365 | 3 | 618 ms | 1,832 ms | $0.0184 | $0.018 |
| Gemini 3.5 Flash Lite | LLM | 1000 | 56.0% | 52.9% to 59.0% | 0.356 | 0.325 | 0 | 681 ms | 805 ms | $0.1158 | $0.116 |
| GPT-5.4 nano | LLM | 1000 | 50.0% | 46.9% to 53.1% | 0.355 | 0.330 | 0 | 708 ms | 1,102 ms | $0.0632 | $0.063 |
| Majority class | baseline | | 27.1% | | | | | | | | |

## Distance from the gold level

Mean absolute distance between the chosen level and the gold level (0 to 4), and the share of answers within one level.

| Model | Mean distance | Within one level |
|---|---|---|
| Jev 1.14 (TypeSafe) | 0.475 | 94.8% |
| Kev-4B | 0.443 | 97.4% |
| Claude Haiku 5.5 | 0.433 | 98.2% |
| Gemini 3.5 Flash Lite | 0.474 | 97.0% |
| GPT-5.4 nano | 0.572 | 93.9% |
| Qwen3.6 35B-A3B | 0.461 | 95.4% |
| Gemma 4 26B-A4B | 0.473 | 95.9% |

## Consistency and thinking

| Model | Run | Result |
|---|---|---|
| Jev 1.14 (TypeSafe) | repeats | 95.0% over 100 decisions |
| Kev-4B | repeats | 100.0% over 100 decisions |
| Claude Haiku 5.5 | repeats | 93.0% over 100 decisions |
| Claude Haiku 5.5 | thinking on (low) | 56.0% on 100 items, against 62.0% with thinking off on the same items; p50 1,285 ms; $0.062 per 1k decisions |
| Gemini 3.5 Flash Lite | repeats | 98.0% over 100 decisions |
| Gemini 3.5 Flash Lite | thinking on (low) | 59.0% on 100 items, against 61.0% with thinking off on the same items; p50 616 ms; $0.112 per 1k decisions |
| GPT-5.4 nano | repeats | 82.0% over 100 decisions |
| GPT-5.4 nano | thinking on (low) | 53.0% on 100 items, against 49.0% with thinking off on the same items; p50 1,744 ms; $0.104 per 1k decisions |
| Qwen3.6 35B-A3B | repeats | 95.0% over 100 decisions |
| Qwen3.6 35B-A3B | thinking on (low) | 63.0% on 100 items, against 63.0% with thinking off on the same items; p50 12,015 ms; $1.299 per 1k decisions |
| Gemma 4 26B-A4B | repeats | 88.0% over 100 decisions |
| Gemma 4 26B-A4B | thinking on (low) | 53.0% on 100 items, against 56.0% with thinking off on the same items; p50 11,252 ms; $0.703 per 1k decisions |
