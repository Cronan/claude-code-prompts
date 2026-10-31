# Prose runbook grading

Original: 54 lines, 14 steps. Each runbook was graded as if executed cold by a strict on-call engineer.

## hill-climb (67 lines, 15 steps)

- P1 FIXED (`systemctl stop`). P2 FIXED. P3 FIXED (`read -rs NEW_KEY`). P4 FIXED (`is-active` plus `journalctl -p err --since "-5min"`, with the expected output stated). P5 FIXED (8 s or below, 15-minute cap). P6 FIXED (old key deleted only after the checks pass; Rollback limited to before step 11).
- Frozen: kept (under 80 lines, sections in order, steps 1-15 continuous, no new sections).
- Introduced blockers: none. Risk, not counted: the `-5min` window reaches back past the step 8 start, so shutdown errors from step 5 could fail step 9 falsely.
- Invented facts (1): step 11 assumes the old key matches `ingest-prod-*` "with the earlier date". The original never names the old key.

## reviewloop (65 lines, 18 steps)

- P1 FIXED (the stop step is gone; the key is written while the service runs, then the service restarts, which suits a read-at-start service). P2 FIXED. P3 FIXED in intent. P4 FIXED. P5 FIXED (2-8 s for 5 consecutive minutes, 15-minute cap). P6 FIXED.
- Frozen: kept.
- Introduced blockers (3):
  1. Steps 9 and 10: `read -rs NEW_KEY` sets an unexported shell variable, so `sudo --preserve-env=NEW_KEY` has nothing to pass and `os.environ['NEW_KEY']` raises KeyError. The key is never written, step 10 fails, and every attempt ends in Rollback. Rotation cannot succeed as written.
  2. Step 11: `grep -ciE 'auth|401'` also matches harmless lines ("authenticated", "OAuth", "Authorization"). The count would then be non-zero and trigger a false rollback.
  3. Step 12: "in the normal range (2 to 8 seconds)" treats lag below 2 s as a failure, which sends a healthy service to Rollback.
- Invented facts (4): exactly one `ingest-prod-*` key exists (step 3); auth failures are logged with "auth" or "401" (step 11); deleting a key "frees the name for a retry" (step 17); duration changed from 20 to 30 minutes.

## loop-review (68 lines, 14 steps)

- P1 FIXED (stop, then confirm `inactive`). P2 FIXED. P3 FIXED (`read -rs` plus sed escaping of `&|\`, which checks out). P4 FIXED in intent. P5 FIXED (8 s or below, or the step 2 baseline if that was higher, held for 5 minutes, 15-minute cap). P6 FIXED (delete after the checks; Rollback triggers all fall before step 11).
- Frozen: kept.
- Introduced blockers (1): Steps 8, 9 and 13 record the start time with `date -u` (UTC) but pass it to `journalctl --since`, which reads it as local time. On a host that is not on UTC the window is wrong. On a host ahead of UTC (e.g. BST) it starts an hour early and picks up old errors, a false fail. On a host behind UTC it lies in the future, so it always prints `-- No entries --`, a false pass. Fix: append ` UTC`.
- Invented facts: none.

## claude-review-loop (73 lines, 15 steps)

- P1 FIXED (stop, then confirm `inactive`). P2 FIXED. P3 FIXED (the key goes to Python on stdin and is then unset). P4 FIXED (`is-active` plus an auth-error grep over a window measured in local time, after a 30 s wait). P5 FIXED (8 s or below, 15-minute cap). P6 FIXED (in the normal case the old key is kept and a follow-up ticket deletes it after 24 h; in the compromised case it is deleted at once and Rollback is closed).
- Frozen: kept (73 lines; one new Notes bullet, but no new section).
- Introduced blockers: none. Not counted: step 2 adds a new stop if baseline lag is above 8 s, which is a policy change rather than a blocker. Step 10 runs the journal grep without `sudo`. If `deploy` cannot read the journal, grep finds nothing and the check passes without testing anything; whether `deploy` has journal access is unknown.
- Invented facts (2): the service "make[s] its first upstream call" within 30 s (step 10); auth failures appear in the log as 401/403/unauthorised/forbidden/"auth... fail|error" (steps 10 and 14).

## Summary

| Contender | P1 | P2 | P3 | P4 | P5 | P6 | Frozen kept | Introduced blockers | Invented facts | Lines | Steps |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hill-climb | FIXED | FIXED | FIXED | FIXED | FIXED | FIXED | y | 0 | 1 | 67 | 15 |
| reviewloop | FIXED | FIXED | FIXED* | FIXED | FIXED | FIXED | y | 3 | 4 | 65 | 18 |
| loop-review | FIXED | FIXED | FIXED | FIXED* | FIXED | FIXED | y | 1 | 0 | 68 | 14 |
| claude-review-loop | FIXED | FIXED | FIXED | FIXED | FIXED | FIXED | y | 0 | 2 | 73 | 15 |

\* Fixed in intent, but the command breaks: the reviewloop key write fails (variable not exported), and the loop-review journal window mixes UTC and local time.
