# Round 1 fix list

Source: reports/round1-reviewer.md (claude -p, model sonnet). All eight findings kept; none classed Skip.

| # | Line(s) | Finding | Class | Action |
|---|---|---|---|---|
| 1 | 24 | Step 5 says "stop" but runs `systemctl restart` | Fix | Change to `stop`; add `is-active` check expecting `inactive` |
| 2 | 28 | sed path `/etc/ingest/keys.yaml` vs live file `/etc/ingest/config/keys.yaml` | Fix | Correct path |
| 3 | 28 | `$NEW_KEY` never set, dropped by sudo env reset, `/` in secret breaks sed, no-match is silent | Fix | `read -rs NEW_KEY`; pass via `sudo NEW_KEY="$NEW_KEY"`; use `|` delimiter; grep to confirm the line changed |
| 4 | 26-29, 47 | Old key overwritten and never recorded; rollback cannot be performed | Fix | Add backup step before edit; rollback restores the backup |
| 5 | 38 | "Verify the rotation worked" has no command or expected result | Fix | `systemctl is-active` = active; journal shows no auth/401 errors. Vendor-specific confirmation not known; left as journal check |
| 6 | 39 | "Acceptable" lag undefined, no timeout | Fix | Lag <= 8 s within 15 min (figures from Notes and Rollback), else Rollback |
| 7 | 40 | Old key deleted immediately; contradicts 24 h rollback window | Fix | Move deletion to after a soak; state rollback is impossible after deletion |
| 8 | 3, 47 | Compromised key: old key stays usable for 24 h | Fix | Compromised branch: delete old key once step 9 passes; no rollback |

Skipped: none.
