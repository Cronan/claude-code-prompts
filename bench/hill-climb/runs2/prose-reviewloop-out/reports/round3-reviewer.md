**Findings, most severe first**

1. **RUNBOOK.md:28 (with 31 and 35): `NEW_KEY` is never exported, so steps 9 and 10 cannot work as written.**
   - `read -rs NEW_KEY` creates a plain shell variable, not an environment variable.
   - `sudo --preserve-env=NEW_KEY` only passes through variables that are already exported. It can also be refused outright by the sudoers policy.
   - Failure scenario:
     - The engineer runs step 8, then step 9. Python raises `KeyError: 'NEW_KEY'` inside the `re.sub` lambda, so the file is not changed.
     - Step 10's check hits the same `KeyError`, prints no `OK`, and sends the engineer to Rollback.
     - The rotation can never succeed, and the engineer has a spent one-time secret and an unexplained failure.

2. **RUNBOOK.md:31 and 51: a failure in step 9 has no failure path.**
   - Rollback is stated for "step 10, 11 or 12" only.
   - Step 9 can fail with the `api_key line not found` assertion, a `KeyError`, or an interrupted `write_text`. `write_text` truncates the file before writing, so an interruption can leave it empty.
   - Failure scenario: step 9 errors, the engineer is told nothing, and either retries on a possibly truncated file or continues to step 10. Nothing says to restore the backup.

3. **RUNBOOK.md:28 and 23: "repeat this step" depends on a secret that was "shown once".**
   - The engineer's SSH session drops after step 8. Step 8 says to repeat it, but the secret exists only in the engineer's clipboard or terminal and cannot be shown again.
   - The runbook does not say to delete the unusable key and create a new one. A same-day replacement would also collide with the `ingest-prod-YYYYMMDD` name.

4. **RUNBOOK.md:39–43: the step 11 health check is unreliable.**
   - `grep -ciE 'auth|401'` matches benign lines such as "authenticated", "authorization cache", or any message containing "401". The engineer then sees a non-zero count on a healthy service and rolls back needlessly.
   - `--since "-1min"` after a 30-second sleep also covers about 30 seconds of the old process's shutdown logs.
   - Conversely, a service that is `active` at 30 seconds can still fail authentication later and show `0`.
   - The text does not say which output line is "the count", and it does not define what a good journal looks like beyond that grep.

5. **RUNBOOK.md:51: the compromised-key rollback path leaves state that breaks later work.**
   - It never removes `keys.yaml.bak`, so the compromised secret stays on disk.
   - Step 7 then refuses every future attempt, because the `.bak` already exists.
   - It skips step 17, so the new key stays live in the console and the live file still contains it.
   - It stops the service with no instruction to restart it later, and no step says when or how to resume.
   - Failure scenario: the engineer follows this path, and the next rotation stops at step 7 with "backup from an earlier attempt exists".

6. **RUNBOOK.md:23–24: the key is created before the pre-flight check, and the step 7 error text is misleading.**
   - If the `.bak` already exists, step 7 says to stop and page, but a new `ingest-prod-*` key was already created in step 6. Nothing says to delete it.
   - The `&&` chain also fails when `cp` fails or `keys.yaml` is missing, yet the prose attributes every non-`OK` result to "a backup from an earlier attempt exists".
   - Failure scenario: an orphaned live key with a secret nobody holds, and a page to the lead with the wrong diagnosis.

7. **RUNBOOK.md:53: "repeat the checks in step 11" is ambiguous.**
   - Step 11's command block is restart, sleep and check in one chain. Repeating "the checks" could mean rerunning the whole block, which restarts the service a second time.
   - Or the engineer runs `is-active` immediately after step 16's own restart, with no wait, and reads a transient `activating` as a failure.
   - Step 16 also deletes the `.bak` on line 55, before the restored state has been verified.

8. **RUNBOOK.md:35: the check assumes the `yaml` module is installed for root's `python3`.**
   - Nothing in Layout or "Before you start" establishes this.
   - Failure scenario: `ModuleNotFoundError`, no `OK`, and the instruction is "go to Rollback". The engineer abandons a correct write.

9. **RUNBOOK.md:51 and 13: the runbook never states that the old key stays valid after the new key is created and until step 13.**
   - Rollback depends on this, and the vendor behaviour is not documented anywhere in the runbook.
   - Failure scenario: if the vendor invalidates or expires the old key on issuing a new one, step 16 restores a dead key and the failure only appears at the second check.

10. **RUNBOOK.md:44 and 18: the lag criterion is incomplete.**
    - The baseline recorded in step 4 is never used. The only pass criterion is "2 to 8 seconds".
    - A lag below 2 seconds, or a backlog drain after restart that exceeds 8 seconds for a while, is treated as failure or left undefined, with no guidance on what to do.

11. **RUNBOOK.md:24 versus Layout line 7: step 7 says to "SSH to the service host".**
    - It omits the `deploy` user and host name that Layout already defines, and Layout says all commands run on that host. This is minor redundancy and inconsistency.
