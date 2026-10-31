# Round 1 fix list

Dedup, challenge and classification of round 1 findings (tester T, builder B, architect A, design critic D). Every cited line was opened in RUNBOOK.md at revision a29dc6a and confirmed unless marked otherwise.

| ID(s) | severity | decision | reason |
|---|---|---|---|
| T-1a, B-1, A-2, D-2 | blocker | Accept | Confirmed: line 22 says "stop", line 24 runs `systemctl restart`; step 8 `start` then is a no-op on a running unit. Fix: `stop`, plus `systemctl is-active` expecting `inactive`. |
| T-1b, B-2a, A-1, D-3a | blocker | Accept | Confirmed: line 28 writes `/etc/ingest/keys.yaml`; lines 9 and 32 use `/etc/ingest/config/keys.yaml`. Fix: correct the literal path in step 6 (smaller than A-1's `$KEY_FILE` variable, which is noted in the backlog). |
| T-2, B-2b, A-4, D-3b | blocker | Accept | Confirmed: `$NEW_KEY` appears only on line 28 and is never set. Fix: `read -rs NEW_KEY` in step 6 with "paste the secret from step 4"; `|` as sed delimiter; step 7 extended to assert `^api_key: $NEW_KEY$` occurs exactly once, so an empty or unset key fails the check. The sudo env_reset concern (T-2, D-3) is wrong: the shell expands `$NEW_KEY` inside the double quotes before sudo runs, so no env passing is needed. |
| T-3, B-3, A-3, D-1, B-4 | blocker | Accept | Confirmed: step 6 overwrites the only copy of the old key; line 40 "delete immediately" contradicts line 47 "stays valid for 24 hours"; step 13 points at a command that writes the new key. Fix: `cp -p` backup before the sed in step 6; step 13 restores from the backup; step 11 deletes the old key only after step 10 passes and removes the backup; 24-hour claim removed. D-1's alternative (paste the old secret into the change ticket) rejected as the fix shape: it puts a live secret in a ticket when an on-host backup suffices. |
| T-4, B-5, A-5, D-4 | high | Accept | Confirmed: lines 38 and 39 are "Verify" and "acceptable" with no command or number; the numbers sit on lines 45 and 54. Fix: step 9 = `is-active` prints `active` and `journalctl -p err --since` returns no lines (generic, needs no author-supplied error string); step 10 = lag <= 8 s for 5 consecutive minutes, else Rollback after 15 min from step 8; Rollback trigger reworded to the same clock. T-4's sed no-op case (missing `api_key:` line) is covered by the step 7 count check. |
| T-5, D-5 | medium | Accept (partial) | Confirmed: line 3 says rotate immediately if compromised but step 13 would reinstate the compromised key; `YYYYMMDD` has no timezone; step 14 names no host or destination for the journal output. Fix: compromise guard in Rollback preamble; "UTC" on the date; host and destination on step 14; `sudo` on journalctl (B out-of-scope note, safe either way). Not fixable from the document alone: the platform lead's pager/channel name (T-5). Goes to Needs your decision. |
| A IDEA (pre-flight writability test) | low | Backlog | Idea, not a confirmed defect; the reviewer labelled it IDEA. |
| A-1 `$KEY_FILE` variable | low | Backlog | Structural improvement beyond the smallest fix; the literal path correction removes the defect. |
| A out-of-scope: 20-minute estimate vs 15-minute wait | low | Reject | Minor, flagged by the reviewer as not structural; the estimate still covers the happy path. |
| T/D out-of-scope: secret in argv and shell history | low | Backlog | Security hardening beyond the goal; noted for the author. |

Accepted: 6 merged findings (18 reviewer IDs). Rejected: 1. Ask: 0 (one sub-item deferred to Needs your decision). Backlog: 3.
