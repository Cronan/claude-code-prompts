# Round 3 fix list

Source: reports/round3-reviewer.md (claude -p, model sonnet).

| # | Line(s) | Finding | Class | Action |
|---|---|---|---|---|
| 1 | 27-29, 72 | Step 6 guard blocks a compromised-key rotation (or any retry) while a legitimate `.bak` from a finished rotation or rollback is still on disk; Notes bullet false | Fix | Ticket-stamped backup name `keys.yaml.bak.<ticket>` so a collision only means a retry of the same ticket; step 14 removes it after a verified restore. The reviewer's "compare live key to backup" remedy is rejected: after a normal rotation they legitimately differ |
| 2 | 29 | Backup chain exits silently when the `.bak` exists; step does not say a missing `OK` means stop | Fix | Say so explicitly |
| 3 | 47, 63 | Bare `401|403` matches PIDs, ports, byte counts | Fix | Anchor with word boundaries and add `unauthori[sz]ed|forbidden` |
| 4 | 47 | `--since "-1min"` not tied to the service start | Fix | Capture `T=$(date '+%F %T')` before `start`; `--since "$T"` in steps 10 and 14 |

Skipped: none.
