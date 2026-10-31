# Round 1 fix list (confirmed blocking and misleading only)

Frozen: under 80 lines; section order Layout, Before you start, Rotation, Rollback, Notes; step numbering continuous.

| # | Section | Line | Defect | Fix |
|---|---|---|---|---|
| 1 | Rotation | step 6, sed command | Overwrites the only copy of the old key; step 13 needs it and the vendor shows a secret once (blocking) | Add `cp -p keys.yaml keys.yaml.bak` before the edit, in the same step |
| 2 | Rotation | step 5, `sudo systemctl restart ingest.service` | Text says stop, command restarts; step 8 `start` is then a no-op and the new key is never loaded (misleading) | Change to `sudo systemctl stop ingest.service` |
| 3 | Rotation | step 6, `/etc/ingest/keys.yaml` | Wrong path; Layout and step 7 use `/etc/ingest/config/keys.yaml` (misleading) | Use `/etc/ingest/config/keys.yaml` |
| 4 | Rotation | step 6, `$NEW_KEY` | Never defined; if unset writes an empty key that step 7 passes (misleading) | Add `read -rs NEW_KEY` (paste the secret) before the sed; step 7 also asserts the file holds the exact key |
| 5 | Rotation | step 6, sed with `/` delimiter and unescaped replacement | `/` in the secret breaks the command; `&` writes a wrong key silently (misleading) | Use `|` as delimiter; step 7 checks `grep -qxF "api_key: $NEW_KEY"` so a mangled write fails rather than passes |
| 6 | Rotation | step 11, "delete the old key immediately" | Contradicts step 13 (old key stays valid 24 h and is the rollback path); after step 11 nothing valid remains to restore (misleading). Policy question: when to delete | Do not delete during the run; record the old key name and delete it after the rollback window; owner to confirm the window |
| 7 | Rollback | step 13, "with the command from step 6" | That command writes `$NEW_KEY`, so it re-applies the new key (misleading) | Restore from the `.bak` copy made in step 6 |
| 8 | Rollback | step 13, "and start the service" | Service may already be running; `start` does not reload the key (misleading) | Use `sudo systemctl restart ingest.service` |

Unchanged-by-fix statements:
- 1: nothing adjacent; adds one command before the existing edit.
- 2: step number and position; only the verb in the command.
- 3: nothing adjacent; path string only.
- 4: step 4 wording about copying the secret; adds a command.
- 5: the sed pattern `^api_key: .*` and the file written; delimiter and step 7 check only.
- 6: step count and numbering; the announcement in step 12.
- 7: the 24-hour fact about the old key; the step number.
- 8: the page in step 14.

Confirmed-at-minor (deferred to end of climb): no change ticket is created or located (steps 2-3); step 9 "Verify the rotation worked" has no command; step 10 "acceptable" lag has no threshold or timeout.
