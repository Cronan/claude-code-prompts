**Findings, most severe first**

1. **RUNBOOK.md:53 – In the compromised-key case, nothing ever revokes the compromised key.**
   - Line 53 says to leave the service stopped and skip to step 17. Step 14 is the only place the old key is deleted, and it is skipped.
   - Failure scenario: the on-call engineer rotates because the key leaked. The new key fails step 12, and they follow line 53. The service is down, and the leaked key stays valid in the Vendor Console because no step tells them to revoke it.

2. **RUNBOOK.md:53 – Rollback is not triggered when logs show auth errors but the unit is `active`.**
   - Line 53 triggers Rollback only if `is-active` fails or step 13 times out. Step 12 also requires "no `authentication` or `401` lines", but the runbook never says what to do when they appear.
   - The check at lines 44–45 is also weak. `-n 50` can include old pre-stop lines, which gives false positives. An auth failure that appears after the 10-second sleep is missed.
   - Failure scenario: the engineer sees `active` plus repeated 401s. The runbook gives no instruction, so they either continue to step 13 and wait up to 15 minutes with the service failing, or improvise.

3. **RUNBOOK.md:35 – Step 10 may not be able to run, and the Layout does not say.**
   - `sudo -u ingest sed -i` creates a temp file in `/etc/ingest/config/`, which needs write access to the directory. The Layout (line 9) gives ownership and mode only for `keys.yaml`, not for the directory.
   - Step 8 runs as root and step 10 runs as `ingest`, so the user is inconsistent. The `deploy` user's sudo rights are also never stated.
   - Failure scenario: the directory is root-owned 0755. `sed` fails with "couldn't open temporary file … Permission denied". The service is already stopped from step 7, so ingest is down until the engineer improvises a fix.

4. **RUNBOOK.md:51–60 – Rollback leaves the new key active and unmanaged.**
   - Rollback never says what to do with the key created in step 6. It stays valid with the `read:feed` scope, and its secret sits in the engineer's shell history or clipboard.
   - The key name `ingest-prod-YYYYMMDD` (line 23) also collides on a same-day retry.
   - Failure scenario: after a rollback, the engineer retries the same day. The Vendor Console rejects the duplicate name, or an orphan credential lingers.

5. **RUNBOOK.md:17, 48 – "Old key" cannot be reliably identified.**
   - `keys.yaml` holds only the secret, while the console lists names. Step 3 tells the engineer to record "the current `ingest-prod-*` key", but nothing maps the live secret to a key name.
   - Failure scenario: a previous rotation left two `ingest-prod-*` keys. The engineer records the wrong one, and step 14 deletes a still-needed key or leaves the real old one valid.

6. **RUNBOOK.md:67 – Backup removal is an action buried in Notes.**
   - It is an unnumbered action placed after the "complete" announcement at step 15, and it breaks continuous step numbering.
   - It does not cover the rollback path, where the `.bak` is redundant, or the compromised path, where the old key stays on disk.
   - Failure scenario: the engineer finishes at step 15 and never reads Notes. A copy of the old secret stays in `/etc/ingest/config/`.

7. **RUNBOOK.md:11, 60, 17–18 – Values the engineer cannot obtain.**
   - No Grafana URL is given, and no pager or contact method for "the platform lead" (lines 16, 60).
   - Failure scenario: at 03:00 the engineer cannot find the dashboard, and cannot page anyone after a failed rollback.

8. **RUNBOOK.md:32–40 – Secret handling and verification are fragile.**
   - `NEW_KEY` exists only in the current shell. If the SSH session drops between step 9 and step 11, the variable is gone and the engineer has to go back to step 6.
   - The secret is never unset, and it is exposed in the `sed` argv.
   - Secrets containing `|`, `&` or `\` corrupt the `sed` replacement.
   - Step 11's YAML check only proves the file parses. It does not confirm that the parsed `api_key` equals the secret, and a missing `yaml` module prints nothing.
   - Failure scenario: a secret with `&` produces a wrong value. The engineer sees `OK` on the parse check and learns about the problem only at step 12 or 13.

9. **RUNBOOK.md:24–30 – Downtime is longer than needed.**
   - The service is stopped (step 7) before the backup (step 8). Line 64 says a restart is enough, so the stop is not required.
   - Failure scenario: the engineer's pasted-secret and verify steps all run while ingest is down, and lag builds for the whole window.

10. **RUNBOOK.md:47, 55 – Verification gaps.**
    - Step 13 accepts a single reading "back in range" with no sustained period, and the step 4 baseline is unused.
    - Rollback step 16 says to repeat step 12, which re-runs `start`, and it has no lag check or failure path if the restored key also fails.
    - Failure scenario: after rollback the engineer sees `active` and stops, but lag never recovers.

11. **RUNBOOK.md:28–30 – A retry can overwrite the backup.**
    - If the engineer re-runs from step 8 without rolling back, `.bak` is overwritten with the already-modified file. The old key is lost, and Rollback restores the new, bad key.

12. **RUNBOOK.md:65–66 – Notes carry text no step uses.**
    - The alert threshold of 60 seconds is never referenced, and the normal-lag range duplicates line 11.
    - Failure scenario: the engineer wonders whether 60 seconds is a rollback trigger. Step 13 says 2–8 seconds, so the guidance conflicts.
