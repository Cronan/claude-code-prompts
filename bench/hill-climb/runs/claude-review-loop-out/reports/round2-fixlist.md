# Round 2 — triage

| # | Finding | Severity | Decision | Reason |
|---|---------|----------|----------|--------|
| 1 | Non-numeric `rate` denies via exception path | LOW | Skip | Correct fail-closed behaviour; constructor validation is out of scope (signatures frozen, validation lives in `load_config`) |
| 2 | Backwards clock guarded by `max(0.0, ...)` | LOW | Skip | Already handled |
| 3 | No bucket entry written on denial for never-admitted key | INFO | Skip | No correctness impact |
| 4 | `"4.0"` string rejected for burst | LOW | Skip | Consistent, not a defect |
| 5 | Thread test uses fixed clock | INFO | Skip | Adequate for the race it targets |

Fix items: none. Stopping rule "no Fix items remain" fires.
