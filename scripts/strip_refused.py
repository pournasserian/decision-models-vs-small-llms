"""Drop rows the gateway refused (rate limit, outage) from result files, so a rerun measures them again."""

import glob
import json
import sys

from bench.runner import refused

pattern = sys.argv[1] if len(sys.argv) > 1 else "results/*/*.jsonl"
for f in glob.glob(pattern):
    rows = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    kept = [r for r in rows if not refused(r)]
    if len(kept) != len(rows):
        with open(f, "w", encoding="utf-8") as out:
            out.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept))
        print(f, len(rows), "->", len(kept))
