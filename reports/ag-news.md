# ag-news

News topic, four options (choice).

Data: AG News test split, fancyzhx/ag_news. 1000 items, 1000 decisions. Majority-class baseline: 26.0%.

| Model | Kind | Items | Accuracy | 95% CI | Brier (top-1) | ECE | Format failures | p50 | p95 | Cost | Per 1k decisions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Kev-4B | decision model | 1000 | 90.0% | 88.0% to 91.7% | 0.073 | 0.039 | 0 | 329 ms | 453 ms | $0.0041 | $0.004 |
| Jev 1.14 (TypeSafe) | decision model | 1000 | 88.3% | 86.2% to 90.1% | 0.086 | 0.054 | 0 | 134 ms | 200 ms | $0.0168 | $0.017 |
| Gemini 3.5 Flash Lite | LLM | 1000 | 87.9% | 85.7% to 89.8% | 0.107 | 0.090 | 0 | 691 ms | 818 ms | $0.1246 | $0.125 |
| Qwen3.6 35B-A3B | LLM | 1000 | 87.7% | 85.5% to 89.6% | 0.103 | 0.083 | 0 | 524 ms | 1,562 ms | $0.0555 | $0.056 |
| Claude Haiku 5.5 | LLM | 1000 | 87.2% | 85.0% to 89.1% | 0.100 | 0.031 | 0 | 1,082 ms | 1,336 ms | $0.0665 | $0.067 |
| Gemma 4 26B-A4B | LLM | 1000 | 82.6% | 80.1% to 84.8% | 0.161 | 0.160 | 0 | 484 ms | 1,239 ms | $0.0196 | $0.020 |
| GPT-5.4 nano | LLM | 1000 | 80.5% | 77.9% to 82.8% | 0.134 | 0.086 | 0 | 681 ms | 995 ms | $0.0679 | $0.068 |
| Majority class | baseline | | 26.0% | | | | | | | | |

## Consistency and thinking

| Model | Run | Result |
|---|---|---|
| Jev 1.14 (TypeSafe) | repeats | 98.0% over 100 decisions |
| Kev-4B | repeats | 100.0% over 100 decisions |
| Claude Haiku 5.5 | repeats | 98.0% over 100 decisions |
| Claude Haiku 5.5 | thinking on (low) | 84.0% on 100 items, against 83.0% with thinking off on the same items; p50 1,174 ms; $0.067 per 1k decisions |
| Gemini 3.5 Flash Lite | repeats | 95.0% over 100 decisions |
| Gemini 3.5 Flash Lite | thinking on (low) | 84.0% on 100 items, against 85.0% with thinking off on the same items; p50 609 ms; $0.120 per 1k decisions |
| GPT-5.4 nano | repeats | 91.0% over 100 decisions |
| GPT-5.4 nano | thinking on (low) | 77.0% on 100 items, against 75.0% with thinking off on the same items; p50 716 ms; $0.075 per 1k decisions |
| Qwen3.6 35B-A3B | repeats | 98.0% over 100 decisions |
| Qwen3.6 35B-A3B | thinking on (low) | 84.0% on 100 items, against 84.0% with thinking off on the same items; p50 6,911 ms; $1.063 per 1k decisions |
| Gemma 4 26B-A4B | repeats | 99.0% over 100 decisions |
| Gemma 4 26B-A4B | thinking on (low) | 80.0% on 100 items, against 77.0% with thinking off on the same items; p50 4,008 ms; $0.158 per 1k decisions |
