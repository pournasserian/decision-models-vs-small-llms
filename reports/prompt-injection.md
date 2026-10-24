# prompt-injection

Is this text a prompt injection? (noul).

Data: deepset/prompt-injections, Apache 2.0, train and test splits. 662 items, 662 decisions. Majority-class baseline: 60.3%.

| Model | Kind | Items | Accuracy | 95% CI | Brier (top-1) | ECE | Format failures | p50 | p95 | Cost | Per 1k decisions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3.6 35B-A3B | LLM | 662 | 92.9% | 90.7% to 94.6% | 0.066 | 0.057 | 0 | 726 ms | 1,773 ms | $0.0353 | $0.053 |
| Gemma 4 26B-A4B | LLM | 662 | 92.9% | 90.7% to 94.6% | 0.069 | 0.067 | 0 | 606 ms | 1,770 ms | $0.0130 | $0.020 |
| Gemini 3.5 Flash Lite | LLM | 662 | 91.1% | 88.7% to 93.0% | 0.089 | 0.089 | 0 | 632 ms | 829 ms | $0.0774 | $0.117 |
| Claude Haiku 5.5 | LLM | 662 | 87.8% | 85.0% to 90.0% | 0.109 | 0.071 | 0 | 1,154 ms | 1,669 ms | $0.0408 | $0.062 |
| Jev 1.14 (TypeSafe) | decision model | 662 | 85.2% | 82.3% to 87.7% | 0.110 | 0.071 | 0 | 127 ms | 180 ms | $0.0099 | $0.015 |
| GPT-5.4 nano | LLM | 662 | 77.0% | 73.7% to 80.1% | 0.203 | 0.184 | 0 | 689 ms | 1,015 ms | $0.0422 | $0.064 |
| Kev-4B | decision model | 662 | 76.6% | 73.2% to 79.7% | 0.144 | 0.111 | 0 | 332 ms | 767 ms | $0.0023 | $0.003 |
| Majority class | baseline | | 60.3% | | | | | | | | |

## Consistency and thinking

| Model | Run | Result |
|---|---|---|
| Jev 1.14 (TypeSafe) | repeats | 99.0% over 100 decisions |
| Kev-4B | repeats | 100.0% over 100 decisions |
| Claude Haiku 5.5 | repeats | 100.0% over 100 decisions |
| Claude Haiku 5.5 | thinking on (low) | 95.0% on 100 items, against 95.0% with thinking off on the same items; p50 1,181 ms; $0.063 per 1k decisions |
| Gemini 3.5 Flash Lite | repeats | 99.0% over 100 decisions |
| Gemini 3.5 Flash Lite | thinking on (low) | 97.0% on 100 items, against 99.0% with thinking off on the same items; p50 621 ms; $0.111 per 1k decisions |
| GPT-5.4 nano | repeats | 100.0% over 100 decisions |
| GPT-5.4 nano | thinking on (low) | 92.0% on 100 items, against 93.0% with thinking off on the same items; p50 912 ms; $0.081 per 1k decisions |
| Qwen3.6 35B-A3B | repeats | 98.0% over 100 decisions |
| Qwen3.6 35B-A3B | thinking on (low) | 97.0% on 100 items, against 97.0% with thinking off on the same items; p50 7,073 ms; $0.987 per 1k decisions |
| Gemma 4 26B-A4B | repeats | 98.0% over 100 decisions |
| Gemma 4 26B-A4B | thinking on (low) | 98.0% on 100 items, against 98.0% with thinking off on the same items; p50 7,411 ms; $0.165 per 1k decisions |
