# Round 2 fix list

Dedup, challenge and classification of round 2 findings against RUNBOOK.md as left by round 1 (68 lines). Line numbers below refer to that version.

| ID(s) | severity | decision | reason |
|---|---|---|---|
| T-1, B-1, A-2, D-2 | high | Accept | Confirmed: line 29 `cp -p` is unguarded and lines 30-32 run regardless of its result; a re-run of step 6 after a failed step 7 would overwrite the good backup with the modified file; step 13 never removes the `.bak`, so a leftover from an earlier rollback would be stale. Fix: step 6 backup becomes `test ! -e .bak && cp -p && echo BACKUP_OK` with "if BACKUP_OK is not printed, stop", step 7 says not to re-run step 6, step 13 removes the `.bak` after restoring. A-2's `cmp` variant rejected as the fix shape: the gate before the write is smaller and stops the overwrite rather than detecting it afterwards. |
| T-2, A-1, D-1 | medium | Accept | Confirmed: line 54 sends the compromised-key case to step 14, which only pages and collects logs; nothing deletes the compromised key and no service state is named. The document already states the priority (line 3: rotate immediately when compromised; original step 11: delete the old key so it cannot be used), so the fix encodes that rather than inventing policy: leave the service stopped, delete the old key in the Vendor Console in step 14, page. The implied acceptance of an outage is recorded under Needs your decision for confirmation. |
| A-3 | medium | Accept | Confirmed: line 16 records a baseline lag that nothing uses; line 48 hard-codes 8 s, so a rotation started while lag is already above 8 s can never pass step 10. Fix: step 10 threshold becomes "8 s, or the step 2 value if that was higher". Smaller than a new gate in step 2 and it still works on the compromised path, where the engineer cannot wait. |
| T-3 | low | Accept | Confirmed locally: `journalctl` with no matches prints `-- No entries --`, so "no log lines" is ambiguous; "note the time" in step 8 is unused and `--since "2 min ago"` can reach back to the stop. Fix: step 8 prints the time with `date -u`, step 9 uses it as `--since` and names `-- No entries --` as the pass output. |
| B-2 | low | Accept | Confirmed: line 56 "repeat step 9" has no stated next action on failure. Fix: "if step 9 fails again, go to step 14". |
| A-5 | low | Accept | Confirmed: step 7 depends on `NEW_KEY` from the step 6 shell; a dropped SSH session triggers a false Rollback. Fix: one phrase in step 6, "same SSH session; if it drops, go to Rollback" (not "restart from step 6", which would collide with the one-backup rule). |
| T-4, B-3, A-4 | low/medium | Ask | Confirmed: after a rollback the step 4 key stays live in the Vendor Console and a same-day retry would reuse its name. Reviewers disagree on the remedy (delete it, or keep it and record the name) and the choice is a credential-handling policy. Not blocking: the rollback path ends with the platform lead paged. |
| T out-of-scope: PyYAML availability for the `ingest` user | unverified | Needs your decision | Cannot be checked from the document. Step 7 was already in the original runbook, so no regression. |
| A out-of-scope: announce rollback in `#ingest-ops` | low | Backlog | Not needed for executability; the platform lead is paged. |
| T out-of-scope: buffered upstream data during the stop/start window | low | Backlog | Operational question for the author, not a document defect. |

Accepted: 6 merged findings (10 reviewer IDs). Rejected: 0. Ask: 1 merged (3 IDs). Backlog: 2. Needs your decision: 1 unverified environment assumption.
