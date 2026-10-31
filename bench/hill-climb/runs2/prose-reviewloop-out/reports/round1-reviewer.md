Findings, most severe first. I checked the file only as written and ran nothing.

1. **RUNBOOK.md:24**: Step 5 says "stop the service" but the command is `systemctl restart`.
   - Scenario: the engineer runs it as written. The service comes straight back up on the old key and keeps running while steps 6 and 7 edit the file. Step 8's `start` then does nothing. The service never reloads the new key, because Notes line 52 says it reads `keys.yaml` only at start. Step 11 then deletes the old key. The running process is now using a revoked key, and lag climbs.

2. **RUNBOOK.md:40, 47**: Step 11 deletes the old key "immediately", but Rollback relies on the old key staying valid for 24 hours.
   - Scenario: lag recovers slowly, the engineer finishes step 11, and lag then blows past 15 minutes. They invoke Rollback and write the old key back. It was already deleted, so the service fails authentication and there is no way back. The "24 hours" claim in line 47 is also unsupported by anything in the forward steps.

3. **RUNBOOK.md:26-28, 47**: The old key is never recorded or located.
   - Step 6 overwrites the `api_key` line in place. Nothing says to save the old value first, and nothing says where it comes from. The Vendor Console shows secrets only once (line 21).
   - Scenario: the engineer reaches Rollback step 13 and has no old key to write back. The runbook gives no way to get it.

4. **RUNBOOK.md:28**: The sed target is `/etc/ingest/keys.yaml`, but Layout (line 9) and step 7 (line 32) use `/etc/ingest/config/keys.yaml`.
   - Scenario: sed fails with "No such file". Step 7 then validates the unchanged real file and prints `OK`, so the engineer believes the key was replaced when it wasn't. If the engineer copies the command into rollback, the same wrong path breaks it too.

5. **RUNBOOK.md:28**: `$NEW_KEY` is never defined.
   - Nothing tells the engineer to set or export it from the secret copied in step 4. It also has to exist in the remote SSH shell, not the browser.
   - Scenario: the variable is empty, so the file gets `api_key: ` with a blank value. Step 7 still passes because empty YAML parses fine, and the service starts with no key.

6. **RUNBOOK.md:38**: Step 9, "Verify the rotation worked", gives no check at all.
   - It names no command, log line or `systemctl is-active` result, and says nothing about what a good result looks like.
   - Scenario: the engineer has nothing to inspect and moves on.

7. **RUNBOOK.md:39**: "Wait until the lag is acceptable" has no number and no time limit.
   - The 2–8 s normal range and 60 s alert threshold sit in Notes (line 54) and are not referenced. The step does not say to compare against the baseline from step 2. Rollback gives 15 minutes (line 45), but step 10 does not.
   - Scenario: the engineer waits indefinitely or moves on at an arbitrary point. Step 11 may then run before the failure is recognised.

8. **RUNBOOK.md:47**: Rollback says "start the service", but the service may already be running (the "lag does not recover" case).
   - Scenario: `start` is a no-op on a running unit, so the old key is never loaded (Notes line 52 says a restart is required). Lag stays bad while the engineer thinks rollback is done.

9. **RUNBOOK.md:40**: Step 11 does not say which key is the "old key".
   - Step 4 names only the new key. The old key's name or ID is never captured.
   - Scenario: the engineer deletes the wrong key, possibly the new one, and takes ingest down.

10. **RUNBOOK.md:17, 41, 48**: `<id>` and the "change ticket" have no source.
    - Nothing says where the ticket id comes from. Step 4 also uses the `YYYYMMDD` placeholder with no timezone. The announcement text is posted literally with `<id>` in it.

11. **RUNBOOK.md:32 (and 28)**: Step 7 only proves the YAML parses. It does not check that `api_key` holds the new value.
    - If the secret contains `/`, `&` or `|`, sed breaks or corrupts the value. If the line is quoted, indented or nested, the pattern silently matches nothing.
    - Scenario: step 7 passes and the old key stays live. Also, `import sys` is unused, and PyYAML availability is assumed.

12. **RUNBOOK.md:3, 47**: The compromised-key path is not handled.
    - The runbook says to rotate immediately for a compromised key, yet Rollback restores the old (compromised) key and leaves it valid for 24 hours.
    - Scenario: during a compromise, a failed rotation puts the leaked key back in service.

13. **RUNBOOK.md:15, 48**: "Page the platform lead" gives no paging method or contact.
    - Scenario: the engineer is locked out of the role or needs to escalate, and cannot find out how to page.
    - Line 48 also asks for `journalctl` output but not to run it with `sudo` or on the service host.

14. **RUNBOOK.md:53**: The `write:feed` history is background, not something any step needs.
    - It is minor scope creep, and the note about the vendor not revoking scopes is unverifiable here.
