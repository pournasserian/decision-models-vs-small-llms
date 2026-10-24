# clinc-domains

Routing to 10 domains plus out of scope (choice).

Data: CLINC150 'plus' test split, CC BY 3.0, domains from clinc/oos-eval. 1000 items, 1000 decisions. Majority-class baseline: 19.0%.

| Model | Kind | Items | Accuracy | 95% CI | Brier (top-1) | ECE | Format failures | p50 | p95 | Cost | Per 1k decisions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Mammoth-1 (Baseten) | decision model | 58 | 82.8% | 71.1% to 90.4% | 0.106 | 0.111 | 0 | 147 ms | 237 ms | $0.0000 | $0.000 |
| Claude Haiku 5.5 | LLM | 1000 | 78.4% | 75.7% to 80.8% | 0.135 | 0.053 | 0 | 1,040 ms | 1,307 ms | $0.0997 | $0.100 |
| Gemini 3.5 Flash Lite | LLM | 1000 | 77.6% | 74.9% to 80.1% | 0.182 | 0.177 | 0 | 634 ms | 765 ms | $0.1860 | $0.186 |
| Jev 1.14 (TypeSafe) | decision model | 1000 | 76.9% | 74.2% to 79.4% | 0.161 | 0.119 | 0 | 139 ms | 216 ms | $0.0268 | $0.027 |
| Gemma 4 26B-A4B | LLM | 1000 | 76.0% | 73.3% to 78.5% | 0.225 | 0.222 | 0 | 589 ms | 1,632 ms | $0.0349 | $0.035 |
| Qwen3.6 35B-A3B | LLM | 1000 | 71.5% | 68.6% to 74.2% | 0.253 | 0.243 | 0 | 736 ms | 1,975 ms | $0.0768 | $0.077 |
| GPT-5.4 nano | LLM | 1000 | 67.3% | 64.3% to 70.1% | 0.197 | 0.152 | 0 | 694 ms | 1,009 ms | $0.1135 | $0.113 |
| Kev-4B | decision model | 1000 | 61.1% | 58.0% to 64.1% | 0.189 | 0.112 | 0 | 344 ms | 462 ms | $0.0120 | $0.012 |
| Majority class | baseline | | 19.0% | | | | | | | | |

## Out of scope

190 of the 1000 requests are out of scope. How often each model said so, how many of the true ones it caught, and its accuracy on the in-scope requests alone.

| Model | Said out of scope | Caught | In-scope accuracy |
|---|---|---|---|
| Jev 1.14 (TypeSafe) | 216 | 121 of 190 | 80.0% |
| Kev-4B | 375 | 136 of 190 | 58.6% |
| Mammoth-1 (Baseten) | 10 | 0 of 190 | 82.8% |
| Claude Haiku 5.5 | 130 | 97 of 190 | 84.8% |
| Gemini 3.5 Flash Lite | 95 | 78 of 190 | 86.2% |
| GPT-5.4 nano | 64 | 46 of 190 | 77.4% |
| Qwen3.6 35B-A3B | 177 | 98 of 190 | 76.2% |
| Gemma 4 26B-A4B | 157 | 107 of 190 | 80.6% |

## Consistency and thinking

| Model | Run | Result |
|---|---|---|
| Jev 1.14 (TypeSafe) | repeats | 100.0% over 100 decisions |
| Kev-4B | repeats | 99.0% over 100 decisions |
| Claude Haiku 5.5 | repeats | 98.0% over 100 decisions |
| Claude Haiku 5.5 | thinking on (low) | 85.0% on 100 items, against 82.0% with thinking off on the same items; p50 1,202 ms; $0.100 per 1k decisions |
| Gemini 3.5 Flash Lite | repeats | 95.0% over 100 decisions |
| Gemini 3.5 Flash Lite | thinking on (low) | 77.0% on 100 items, against 82.0% with thinking off on the same items; p50 596 ms; $0.181 per 1k decisions |
| GPT-5.4 nano | repeats | 94.0% over 100 decisions |
| GPT-5.4 nano | thinking on (low) | 71.0% on 100 items, against 73.0% with thinking off on the same items; p50 727 ms; $0.119 per 1k decisions |
| Qwen3.6 35B-A3B | repeats | 98.0% over 100 decisions |
| Qwen3.6 35B-A3B | thinking on (low) | 79.0% on 100 items, against 75.0% with thinking off on the same items; p50 8,404 ms; $1.182 per 1k decisions |
| Gemma 4 26B-A4B | repeats | 96.0% over 100 decisions |
| Gemma 4 26B-A4B | thinking on (low) | 81.0% on 100 items, against 81.0% with thinking off on the same items; p50 4,827 ms; $0.212 per 1k decisions |
