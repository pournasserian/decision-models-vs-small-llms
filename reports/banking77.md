# banking77

Intent routing with 77 options (choice).

Data: Banking77, PolyAI, CC BY 4.0, test split. 1000 items, 1000 decisions. Majority-class baseline: 2.0%.

| Model | Kind | Items | Accuracy | 95% CI | Brier (top-1) | ECE | Format failures | p50 | p95 | Cost | Per 1k decisions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Mammoth-1 (Baseten) | decision model | 983 | 92.9% | 91.1% to 94.3% | 0.048 | 0.019 | 0 | 220 ms | 518 ms | $0.0000 | $0.000 |
| Kev-4B | decision model | 1000 | 86.0% | 83.7% to 88.0% | 0.137 | 0.169 | 0 | 383 ms | 548 ms | $0.0327 | $0.033 |
| Gemini 3.5 Flash Lite | LLM | 1000 | 81.7% | 79.2% to 84.0% | 0.164 | 0.163 | 0 | 652 ms | 782 ms | $0.2540 | $0.254 |
| Jev 1.14 (TypeSafe) | decision model | 1000 | 80.2% | 77.6% to 82.6% | 0.118 | 0.075 | 0 | 149 ms | 223 ms | $0.0677 | $0.068 |
| Claude Haiku 5.5 | LLM | 1000 | 78.9% | 76.3% to 81.3% | 0.132 | 0.046 | 0 | 1,101 ms | 1,354 ms | $0.2049 | $0.205 |
| GPT-5.4 nano | LLM | 1000 | 76.9% | 74.2% to 79.4% | 0.157 | 0.090 | 0 | 717 ms | 1,024 ms | $0.2200 | $0.220 |
| Gemma 4 26B-A4B | LLM | 1000 | 76.2% | 73.5% to 78.7% | 0.204 | 0.203 | 0 | 665 ms | 1,585 ms | $0.0546 | $0.055 |
| Qwen3.6 35B-A3B | LLM | 1000 | 71.3% | 68.4% to 74.0% | 0.207 | 0.198 | 40 | 785 ms | 1,890 ms | $0.1106 | $0.111 |
| Majority class | baseline | | 2.0% | | | | | | | | |

## Consistency and thinking

| Model | Run | Result |
|---|---|---|
| Jev 1.14 (TypeSafe) | repeats | 97.0% over 100 decisions |
| Kev-4B | repeats | 100.0% over 100 decisions |
| Claude Haiku 5.5 | repeats | 95.0% over 100 decisions |
| Claude Haiku 5.5 | thinking on (low) | 82.0% on 100 items, against 81.0% with thinking off on the same items; p50 1,173 ms; $0.207 per 1k decisions |
| Gemini 3.5 Flash Lite | repeats | 98.0% over 100 decisions |
| Gemini 3.5 Flash Lite | thinking on (low) | 80.0% on 100 items, against 81.0% with thinking off on the same items; p50 714 ms; $0.242 per 1k decisions |
| GPT-5.4 nano | repeats | 85.0% over 100 decisions |
| GPT-5.4 nano | thinking on (low) | 85.0% on 100 items, against 80.0% with thinking off on the same items; p50 837 ms; $0.240 per 1k decisions |
| Qwen3.6 35B-A3B | repeats | 84.0% over 100 decisions |
| Qwen3.6 35B-A3B | thinking on (low) | 75.0% on 100 items, against 66.0% with thinking off on the same items; p50 6,907 ms; $1.236 per 1k decisions |
| Gemma 4 26B-A4B | repeats | 94.0% over 100 decisions |
| Gemma 4 26B-A4B | thinking on (low) | 72.0% on 100 items, against 73.0% with thinking off on the same items; p50 9,977 ms; $0.427 per 1k decisions |
