1. CONFIRMED AT minor. Steps 2 and 3 refer to "the change ticket" and `<id>`, and nothing creates or locates one. "The" implies an existing ticket that the on-call would already have, so this is a gap in wording, not a blocker.

2. CONFIRMED AT misleading. Step 5 says "stop" but runs `restart`, so the service is running when step 8 runs `start`, which does nothing. The Notes say keys are read only at start, so the new key is never loaded.

3. CONFIRMED AT misleading. Step 6 targets `/etc/ingest/keys.yaml`, but Layout and step 7 use `/etc/ingest/config/keys.yaml`. Step 7 validates the unchanged correct file and prints OK, a false pass.

4. CONFIRMED AT misleading. `$NEW_KEY` is never set. Step 4 only says to copy the secret. If it is unset, step 6 writes an empty `api_key`, which is still valid YAML, so step 7 passes.

5. CONFIRMED AT misleading. The sed replacement is unescaped. A `/` in the secret breaks the command, and `&` is replaced by the matched text, so a wrong key is written silently. The runbook never states the key's character set.

6. CONFIRMED AT blocking. Step 6 overwrites the only copy of the old key, and no step backs it up. Step 13 needs that value, and nothing says how to retrieve it.

7. CONFIRMED AT minor. Step 9 has no command or expected output. Intent can be inferred from "service fails to start" in Rollback and the lag check in step 10, so the on-call can improvise a check.

8. CONFIRMED AT minor. Step 10 gives no threshold of its own. Notes give normal lag as 2 to 8 seconds and the alert threshold as 60 seconds, and Rollback gives a 15-minute limit. The step just doesn't point to them.

9. CONFIRMED AT misleading. Step 11 deletes the old key immediately, while step 13 says it "stays valid for 24 hours", so any rollback after step 11 has no key to restore. It is not blocking, because the rollback trigger comes before step 11 and step 10 gates it.

10. CONFIRMED AT misleading. The step 6 command uses `$NEW_KEY` and the wrong path. Run as written, it re-applies the new key (or an empty one) and does not restore the old one.

11. CONFIRMED AT misleading. In the lag-does-not-recover case the service is already running, so `start` does nothing and the restored key is never read. Only a restart reloads it, per the Notes.
