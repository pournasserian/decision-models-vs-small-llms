# Summary

Generated 2026-10-26. Accuracy per task, majority baseline in the last row. Each task's own report has the confidence intervals, calibration, latency and cost.

| Model | Kind | banking77 | clinc-domains | prompt-injection | sst5 | ag-news | typed-decisions | Mean |
|---|---|---|---|---|---|---|---|---|
| Jev 1.14 (TypeSafe) | decision model | 80.2% | 76.9% | 85.2% | 58.1% | 88.3% | 74.6% | 77.2% |
| Kev-4B | decision model | 86.0% | 61.1% | 76.6% | 58.6% | 90.0% | 66.8% | 73.2% |
| Laya 421M | decision model | – | 29.6% | 79.5% | 31.3% | 92.4% | 35.4% | 53.6% |
| Mammoth-1 (Baseten) | decision model | 93.0% | 83.0% | 26.0% | 49.7% | 0.0% | – | 50.3% |
| Claude Haiku 5.5 | LLM | 78.9% | 78.4% | 87.8% | 58.7% | 87.2% | 72.7% | 77.3% |
| Gemini 3.5 Flash Lite | LLM | 81.7% | 77.6% | 91.1% | 56.0% | 87.9% | 71.5% | 77.6% |
| GPT-5.4 nano | LLM | 76.9% | 67.3% | 77.0% | 50.0% | 80.5% | 66.8% | 69.8% |
| Qwen3.6 35B-A3B | LLM | 71.3% | 71.5% | 92.9% | 59.0% | 87.7% | 67.4% | 75.0% |
| Gemma 4 26B-A4B | LLM | 76.2% | 76.0% | 92.9% | 57.0% | 82.6% | 74.6% | 76.5% |
| Majority class | baseline | 2.0% | 19.0% | 60.3% | 27.1% | 26.0% | 46.1% | |

## Latency, cost and failures

Median latency over all tasks, cost per 1,000 decisions over all tasks, and format failures in total.

| Model | p50 | p95 | Per 1k decisions | Format failures | Decisions |
|---|---|---|---|---|---|
| Jev 1.14 (TypeSafe) | 139 ms | 209 ms | $0.023 | 0 | 6662 |
| Kev-4B | 333 ms | 502 ms | $0.009 | 0 | 6662 |
| Laya 421M | 400 ms | 1,126 ms | $0.000 | 8 | 5662 |
| Mammoth-1 (Baseten) | 164 ms | 496 ms | $0.000 | 736 | 3799 |
| Claude Haiku 5.5 | 1,111 ms | 1,472 ms | $0.085 | 0 | 6662 |
| Gemini 3.5 Flash Lite | 666 ms | 863 ms | $0.146 | 0 | 6662 |
| GPT-5.4 nano | 709 ms | 1,111 ms | $0.091 | 0 | 6662 |
| Qwen3.6 35B-A3B | 713 ms | 2,243 ms | $0.064 | 49 | 6662 |
| Gemma 4 26B-A4B | 618 ms | 2,156 ms | $0.027 | 3 | 6662 |

Total spent across every run in `ledger.csv`: $5.97.
