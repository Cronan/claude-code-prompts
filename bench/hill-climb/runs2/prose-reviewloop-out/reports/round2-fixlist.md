# Round 2 fix list

Source: reports/round2-reviewer.md (12 findings). Disposition of each:

1. Compromised key never revoked on the rollback path -> Rollback preamble now says: if compromised, delete the old key in the Vendor Console (as in the deletion step), leave the service stopped, page.
2. Auth errors with `active` unit has no instruction; `-n 50` can include pre-stop lines -> restart step now reads logs with `--since "-1min"` and counts `auth|401` lines (expect `0`); "if either check fails, go to Rollback" stated in the step and in the Rollback trigger.
3. `sudo -u ingest sed -i` needs directory write access; user inconsistency; `deploy` sudo rights unstated -> all privileged commands now run via plain `sudo` (root); the in-place write uses Python `write_text` on the existing inode so owner/mode are untouched, and a `stat` check asserts `ingest:ingest 600`; Layout states `deploy` has sudo (the original runbook already relied on it).
4. Rollback leaves the new key live; same-day name collision -> Rollback step deletes the new key in the Vendor Console, which also clears the name for a retry.
5. Old key cannot be identified if several `ingest-prod-*` keys exist -> step 3 now says: expect exactly one; if more than one, stop and page before changing anything.
6. Backup removal buried in Notes -> promoted to a numbered step before the completion announcement; Rollback removes it after restoring; Notes entry removed.
7. No Grafana URL, no pager method -> rejected (second time). Both are organisational knowledge the on-call engineer has independently of this runbook; inventing a URL or a contact would be fabrication. Recorded in the final report as a residual.
8. Secret handling: `NEW_KEY` lost on SSH drop, never unset, exposed in argv, sed metacharacters, YAML check does not compare value -> sed replaced by Python with the secret passed via environment (`sudo --preserve-env`), replacement via lambda so no metacharacters are interpreted; verification parses the YAML and compares `api_key` to the secret; `unset NEW_KEY` after verification; instruction to repeat the read step if the session drops.
9. Service stopped before backup; Notes says restart suffices -> separate stop and start replaced by one `systemctl restart` after the file is written and verified. The service stays up on the old key until the new file is proven good.
10. Step 13 single reading; baseline unused; rollback has no lag check -> lag must stay in range for 5 consecutive minutes within the 15-minute window; 60-second alert threshold is now an immediate rollback trigger; rollback repeats the restart checks and the lag watch.
11. Retry overwrites `.bak` -> backup step refuses to overwrite an existing `.bak` (must print `OK`); if it does not, stop and page.
12. Notes duplicates normal range; 60 s threshold unused -> duplicate removed from Layout; threshold used in step 13.
