I found four defects in the changed lines. I read `RUNBOOK.md` only and didn't run any of the commands.

1. **`RUNBOOK.md:27-29` and `RUNBOOK.md:72`, high.** The step 6 guard treats any existing `keys.yaml.bak` as an interrupted run. The runbook itself creates leftover `.bak` files in two cases:
   - After a normal rotation, step 12 leaves the `.bak` for 24 hours or more.
   - After a completed Rollback, nothing removes it.

   A compromised-key rotation started within that window is blocked at step 6, which is the case that must go immediately. A retry after a rollback is blocked too. The last Notes bullet ("its presence at step 6 means a previous run did not finish") is therefore false.
   - **Fix:**
     - Have step 14 remove the `.bak` once the restore is verified.
     - In step 6, if the `.bak` exists and the live `api_key` matches it, treat it as a leftover and continue. If they differ, stop and page.
     - Alternatively, use a ticket-stamped backup name.

2. **`RUNBOOK.md:29`, medium.** When the `.bak` already exists, the `test ! -e … && …` chain prints nothing and exits 1. That looks the same as a pasted command that did nothing. The step also doesn't say that a missing `OK` means stop.
   - **Fix:** Add "If `OK` is not printed, stop. Do not continue to step 7." Or add `|| { echo BACKUP-EXISTS; false; }` to the chain.

3. **`RUNBOOK.md:47` and `RUNBOOK.md:63`, medium.** The bare `401|403` pattern matches any line containing those digits, such as a PID, port, byte count or timestamp fragment. A false positive sends a healthy rotation to Rollback. The same grep serves as the pass check in step 14, so a false positive there pages the lead needlessly.
   - **Fix:** Anchor it, for example `grep -Ei '\b(HTTP|status)[ :=]*(401|403)\b|unauthori[sz]ed|forbidden|auth[a-z]* *(fail|error)'`, or match the service's actual log wording.

4. **`RUNBOOK.md:47`, low-medium.** `--since "-1min"` isn't tied to the moment the service started. If steps 5 to 10 run in under a minute (quick, or scripted), the window also covers the old process's shutdown lines. After a `sleep 30` it also depends on timing slack.
   - **Fix:** Capture `T=$(date '+%F %T')` immediately before `systemctl start`, then use `--since "$T"` in both step 10 and step 14.
