# Round 2 fix list

Source: reports/round2-reviewer.md (claude -p, model sonnet).

| # | Line(s) | Finding | Class | Action |
|---|---|---|---|---|
| 1 | 37 | Secret expanded on the `sudo sed` command line: lands in sudo log and `ps` | Fix | Replace sed and grep with a python one-liner that reads the key from stdin and prints the replacement count; `unset NEW_KEY` after. Also removes the sed special-character caveat |
| 2 | 35-43 | No failure path if the write (step 8) or parse check (step 9) fails while the service is down | Fix | Rollback trigger widened to cover steps 8 to 11 |
| 3 | 44, 48 | `journalctl -n 50` includes pre-restart lines, may run before first auth call, bare `auth` matches benign lines | Fix | `--since` the start, wait 30 s, grep for `401|403|auth.*(fail|error)` |
| 4 | 58-63 | Rollback never verifies the service came back | Fix | Add `is-active` and lag check; page if either fails |
| 5 | 29 | `cp -p` overwrites an existing `.bak` on a re-run, destroying the old key | Fix | Stop if `.bak` already exists |
| 6 | 51, 71 | `.bak` deletion stated in Notes but not performed in either step 12 branch | Fix | `rm` in compromised branch; include in follow-up ticket text |
| 7 | 56-64 | New vendor key left active after rollback | Skip | Hygiene, not a defect that blocks or misleads the engineer; not needed for a correct rotation or rollback |
