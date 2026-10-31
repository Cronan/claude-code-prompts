# Round 1 fix list

Source: reports/round1-reviewer.md (14 findings). Disposition of each:

1. Step 5 `restart` vs "stop" -> command changed to `systemctl stop`.
2. Step 11 deletes old key before rollback window closes; "24 hours" unsupported -> old-key deletion moved to after the 15-minute observation window; "24 hours" claim removed; rollback now states it is only possible while the old key still exists, and what to do if it has already been deleted.
3. Old key never recorded -> new step backs up `keys.yaml` (with `cp -p`, so owner and mode are kept) before editing; rollback restores the backup rather than asking the engineer for the old secret.
4. sed path `/etc/ingest/keys.yaml` -> `/etc/ingest/config/keys.yaml`, matching Layout.
5. `$NEW_KEY` undefined -> step added: on the service host, `read -rs NEW_KEY` then paste the secret (keeps it out of shell history).
6. Step 9 has no check -> replaced with `systemctl is-active` (expect `active`) and a `journalctl` tail with what good looks like.
7. Step 10 unbounded wait -> wait up to 15 minutes for lag to return to the normal range (2 to 8 s, quoted in the step); otherwise go to Rollback.
8. Rollback `start` is a no-op if running -> rollback uses `systemctl restart`.
9. "Old key" never identified -> before creating the new key, record the name of the current `ingest-prod-*` key in the ticket; deletion step names it.
10. `<id>` / change ticket has no source; `YYYYMMDD` timezone -> Before you start now opens with raising the change ticket (or using the incident ticket if compromised) and defines `<id>`; date stated as today's UTC date.
11. Step 7 only parses YAML; sed delimiter fragility -> sed uses `|` as delimiter and step 7 greps for the exact `api_key: $NEW_KEY` line before parsing; unused `import sys` removed.
12. Compromised-key path: rollback would restore the leaked key -> rollback says not to restore a compromised key; leave the service stopped and page.
13. "Page the platform lead" has no method -> journalctl now run with `sudo` on the service host. Paging mechanism NOT added: how to page is the on-call engineer's standing organisational knowledge, not runbook-specific, and inventing a contact or tool would be fabrication. Recorded as rejected.
14. `write:feed` note is scope creep -> rejected: it is pre-existing content that justifies the `read:feed` constraint in the key-creation step; acceptance item 7 concerns changes made by this loop, not the original text.
