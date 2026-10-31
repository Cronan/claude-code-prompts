# Round 2 fix list (confirmed blocking and misleading only)

Frozen: under 80 lines; section order Layout, Before you start, Rotation, Rollback, Notes; step numbering continuous.

| # | Section | Line | Defect | Fix |
|---|---|---|---|---|
| 1 | Rotation | step 7, `&& echo OK` | No instruction if OK is not printed; service is stopped and Rollback does not cover this case (blocking) | Add "If OK is not printed, go to step 13" and add a failed step 7 to the Rollback trigger line |
| 2 | Rotation | step 9, "Verify the rotation worked." | No command, no expected result (misleading) | `systemctl is-active ingest.service` prints `active`; `sudo journalctl -p err -u ingest.service --since "-5min"` prints no lines; otherwise go to step 13 |
| 3 | Rotation + Rollback | step 10 "acceptable"; Rollback "does not recover within 15 minutes" | No threshold, no start point (misleading) | Threshold 8 s, the top of the normal range already in Notes; clock starts at step 8; state both in step 10 and in the Rollback trigger |
| 4 | Rotation | step 11, "OWNER TO SET" placeholder | No deletion time or owner; old key left live (misleading) | Remove the placeholder. Rollback is only reachable before step 11 (steps 7, 8, 10 gate it), so delete the old key in step 11 once step 10 has passed, as the author originally intended, and state in Rollback that it applies only before step 11 |
| 5 | Rollback | step 13 | Does not check rollback worked, announce it, or revoke the new key (misleading) | After the restart, repeat the step 9 check; new step: delete the new key in the Vendor Console and announce the rollback in `#ingest-ops` |
| 6 | Rollback | step 13 reachable after the old key is deleted | Would restore a dead key (misleading) | Scope the Rollback section: applies before step 11 only; after that a failure is a new incident, page the platform lead |

Unchanged-by-fix statements:
- 1: the step 7 command; adds a sentence and extends the trigger line.
- 2: step 9's position and number; replaces its one sentence with a check.
- 3: the Notes figures (2 to 8 s, 60 s); adds the number to two existing sentences.
- 4: step count stays continuous; step 12 announcement unchanged; the 24-hour fact in step 13.
- 5: the restore and restart commands in step 13; the page in step 14 keeps its content; adds a step 15.
- 6: nothing adjacent; one sentence added to the Rollback intro.

Confirmed-at-minor (deferred): no step creates or locates the change ticket (steps 2-3); no Grafana URL in Layout.
