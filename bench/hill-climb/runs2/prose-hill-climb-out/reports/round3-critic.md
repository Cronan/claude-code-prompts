**1 blocking, 5 misleading, 5 minor**

**Layout:** No problems on its own. Two findings below depend on things it doesn't state.

**Before you start**
- **Blocking.** Step 2, "Record it in the change ticket", and step 3, "ticket <id>". The runbook never says which ticket system to use, whether a ticket already exists, or where the id comes from. I can't post step 3, 12 or 14 without asking. *Fix:* "Create a change ticket in <system> (or use the page's incident id); use its id below."
- **Minor.** Step 2, "note the current consumer lag". The value is never used again, and "current" has no time window. *Fix:* say what it is compared against, or drop it.
- **Minor.** The section never checks SSH as `deploy`, `sudo -u ingest`, or that `ingest` can write to `/etc/ingest/config/` (both `cp` and `sed -i` need that). If any of these fails after step 4, I hold a new key with no instruction. *Fix:* add a pre-check, e.g. `ssh deploy@ingest-01.prod.internal 'sudo -u ingest test -w /etc/ingest/config && echo OK'`.

**Rotation**
- **Misleading.** Step 11, "delete the old key (the `ingest-prod-*` key with the earlier date)". This assumes exactly two such keys exist and that the old key follows the naming pattern. If there are several older keys, a legacy-named key, or two keys with the same date, I could delete the wrong one. *Fix:* in step 4, "Before creating, record the name of the key currently in use in the ticket", and have step 11 delete that name.
- **Misleading.** Step 7, `python3 -c "import yaml,sys; ..."`. Nothing confirms PyYAML is installed. An `ImportError` means no `OK`, which sends a good key into rollback. *Fix:* add `python3 -c 'import yaml'` to the pre-checks.
- **Misleading.** Step 6, `sed -i "s|^api_key: .*|api_key: $NEW_KEY|"`. A secret containing `|`, `&` or `\` breaks or corrupts the substitution. A secret with YAML-significant characters (`#`, `: `, a leading `*` or `&`) parses to a different value, and step 7's parse check doesn't catch that. *Fix:* state the vendor's secret character set, or write the line with a tool that quotes it (e.g. a Python one-liner that dumps YAML).
- **Misleading.** Step 9, `journalctl ... --since "-5min"`. The 5-minute window can include errors from the shutdown in step 5, which fails the check falsely. It also runs straight after start, before auth errors may have appeared. *Fix:* `--since "<step 8 time>"`, run 60 seconds after step 8.
- **Minor.** Step 10, "Continue when lag is 8 seconds or below". After the restart, lag falls through 8 on its way down, so one reading at or below 8 lets me continue before it has settled. *Fix:* "at or below 8 s for 3 consecutive minutes."
- **Minor.** Step 6, `read -rs NEW_KEY` then `sed ... $NEW_KEY`. The secret ends up in the `sed` command line, where `ps` shows it, and `keys.yaml.bak` keeps the old secret after step 11. *Fix:* add a cleanup step, `sudo -u ingest rm /etc/ingest/config/keys.yaml.bak`, after step 11.
- **Minor.** Step 8, "note the time". It doesn't say where to record it. *Fix:* "record it in the ticket."

**Rollback**
- **Misleading.** Step 13, "repeat the step 9 checks". When rollback was triggered by step 9 or step 10, the error lines from the failed new-key run are still inside the `-5min` window. The re-check therefore fails even when the restore worked, and step 15 reports it wrong. *Fix:* use `--since "<step 13 restart time>"` for the re-check.
- **Minor.** Step 13, "the old key stays valid for 24 hours after rotation" conflicts with step 11, "delete the old key so it cannot be used". Step 11 implies the old key never expires on its own, and "rotation" (create time? step 8?) is undefined. That doesn't change any action inside the 15-minute window. *Fix:* "the old key stays valid until deleted in step 11."

Apart from those two findings, the rollback works: the `.bak` copy holds the old key, the old key is still valid before step 11, and a restart reloads it.

**Notes:** No problems; consistent with the other sections.
