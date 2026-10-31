**Findings for RUNBOOK.md** (one commit, new file)

1. **`RUNBOOK.md:24`, Critical.** Step 5 says "stop the service" but the command is `restart`.
   - The service restarts and loads the old key. After step 6 edits the file, step 8's `start` does nothing because the unit is already running.
   - The Notes say keys are read only at start, so the service keeps using the old key. Step 11 then deletes that key and ingest breaks.
   - **Fix:** change the command to `sudo systemctl stop ingest.service`. Add `systemctl is-active` (expect `inactive`) before editing.

2. **`RUNBOOK.md:28`, High.** The path is wrong. It uses `/etc/ingest/keys.yaml`, but the live file is `/etc/ingest/config/keys.yaml` (lines 9 and 32).
   - `sed -i` fails on a missing file, so the new key is never written. If the failure is missed, step 8 starts the service with the old key.
   - **Fix:** use `/etc/ingest/config/keys.yaml`.

3. **`RUNBOOK.md:28`, High.** `$NEW_KEY` is never defined, and the command is fragile.
   - Nothing in step 4 says to export it. `sudo` also resets the environment, so the variable would be empty even if it were set. Without a real value the line becomes `api_key: `.
   - A secret containing `/`, `&` or `\` breaks the `sed` expression.
   - `sed` exits 0 when `^api_key:` doesn't match, so a failed substitution is silent.
   - **Fix:** read the key without echoing it (`read -rs NEW_KEY`). Pass it through `sudo` explicitly (`sudo NEW_KEY="$NEW_KEY" -u ingest ...`) and use a safe delimiter or escape the value. Follow with `grep -c '^api_key: ' <file>` to confirm the line is present.

4. **`RUNBOOK.md:26-29`, High.** The old key is never saved.
   - Rollback (line 47) says to "write it back", but the `sed` overwrite destroys it and nothing in the runbook tells the engineer to record it. Rollback can't be done as written.
   - **Fix:** add a step before editing: `sudo -u ingest cp -p keys.yaml keys.yaml.bak.$(date +%Y%m%d)`. Make rollback restore that file.

5. **`RUNBOOK.md:38`, High.** "Verify the rotation worked" has no command or expected result.
   - **Fix:** give concrete checks. For example, `systemctl is-active ingest.service` returns `active`, `journalctl -u ingest.service -n 50` shows no auth errors, and a named log line or API call confirms the new key authenticates.

6. **`RUNBOOK.md:39`, Medium.** "Lag is acceptable" is undefined, and there is no timeout.
   - Rollback (line 45) uses 15 minutes, but step 10 doesn't say so, so the engineer can wait forever or proceed too early.
   - **Fix:** write "wait up to 15 min for lag ≤ 8 s (normal 2–8 s; alert at 60 s). If not met, go to Rollback." Also say what to do if the lag was already high in step 2.

7. **`RUNBOOK.md:40`, Critical.** Deleting the old key "immediately" breaks rollback.
   - Line 47 says the old key stays valid for 24 hours, and rollback depends on that. Once step 11 runs, rollback is impossible. Lag can also regress after step 11.
   - **Fix:** do not delete the old key in this procedure's main flow. Add a follow-up step to delete it after about 24 hours of healthy operation, or after the lag check passes with a stated soak period. Add a warning that rollback is not possible after deletion.

8. **`RUNBOOK.md:3` and `47`, Medium.** The compromised-key case isn't handled.
   - It says to rotate immediately, but the old key stays valid for 24 hours, so the compromised key is still usable.
   - **Fix:** add a compromised-key branch. Delete or disable the old key right after verification, and note that rollback is not available in that case.
