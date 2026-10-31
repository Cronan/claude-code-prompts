5 blocking, 6 misleading, 3 minor

**Layout:** no problems. Every mismatch is in a step that ignores it.

**Before you start**
- **Blocking.** Steps 2–3, "Record it in the change ticket" / "ticket <id>". No step creates a ticket or says where to find one, and being paged doesn't mean one exists. Fix: add "Open a change ticket in <system> (or use the incident ticket) and note its id."

**Rotation**
- **Misleading.** Step 5, "stop the service" vs `sudo systemctl restart ingest.service`. The command restarts the service, so it keeps running with the old key. Step 8's `start` then does nothing, and the new key is never loaded (Notes: "reads keys.yaml only at start"). Steps 9–10 would be checking the old key. Fix: `sudo systemctl stop ingest.service`.
- **Misleading.** Step 6, `/etc/ingest/keys.yaml`. Layout says the file is `/etc/ingest/config/keys.yaml`. `sed` fails on the wrong path, but step 7 checks the correct path, prints OK on the unchanged file, and invites you to continue. Fix: use `/etc/ingest/config/keys.yaml`.
- **Misleading.** Step 6, `$NEW_KEY`. It's never defined. If unset, it writes `api_key: ` with no value, and step 7 still prints OK because an empty value is valid YAML. Fix: add "`read -rs NEW_KEY` and paste the secret from step 4", and make step 7 also assert the key is non-empty.
- **Misleading.** Step 6, `sed -i "s/^api_key: .*/api_key: $NEW_KEY/"`. A secret containing `/` breaks the command. One containing `&` silently writes the wrong key. Fix: use a different delimiter and escape `&`, or write the file with a templating or `yq` command.
- **Blocking.** Step 6 overwrites the file in place without saving the old value, and the vendor shows a secret only once (step 4). Step 13 needs that old key, and it's gone. Fix: before step 6, `sudo -u ingest cp -p /etc/ingest/config/keys.yaml /etc/ingest/config/keys.yaml.bak`.
- **Blocking.** Step 9, "Verify the rotation worked." There's no command or expected output. Fix: e.g. "`systemctl is-active ingest.service` returns `active`, and `journalctl -u ingest.service -n 50` shows no auth errors" (state the actual success log line).
- **Blocking.** Step 10, "wait until the lag is acceptable." There's no threshold, and it doesn't say whether to compare against step 2's baseline or the Notes' "2 and 8 seconds" / "60 seconds". It has no timeout either. Fix: "Continue when lag is ≤ 8 s (or ≤ baseline) for 5 consecutive minutes. If not within 15 min of step 8, go to Rollback."
- **Blocking.** Step 11, "delete the old key immediately," contradicts step 13, "the old key stays valid for 24 hours after rotation." After step 11 the rollback has nothing valid to restore. Fix: "Do not delete the old key until 24 h after rotation, unless it is compromised. Schedule the deletion in the ticket."
- **Minor.** Step 11, "the old key." It doesn't say how to identify it among the console's keys. Fix: "the `ingest-prod-*` key with the previous date (record its name in the ticket at step 4)."
- **Minor.** Step 4, `YYYYMMDD`. It doesn't say whether that's the UTC or local date, and at 02:10 UTC the two can differ. Fix: "UTC date."

**Rollback**
- **Minor.** "lag does not recover within 15 minutes." The clock has no start point, and "recover" has no threshold. Fix: "within 15 minutes of step 8, to ≤ 8 s."
- **Misleading.** Step 13, "with the command from step 6." That command uses `$NEW_KEY` and the wrong path, so run as written it puts the new key back in place. Fix: "`sudo -u ingest cp -p /etc/ingest/config/keys.yaml.bak /etc/ingest/config/keys.yaml`."
- **Misleading.** Step 13, "and start the service." If the service is running on the bad key, `start` does nothing and the restored key is never read. Fix: `sudo systemctl restart ingest.service`.
- **Minor.** Step 14, `journalctl -u ingest.service -n 200`. As `deploy`, this may show nothing without `sudo` or membership in the `systemd-journal` group. Fix: prefix with `sudo`.

**Notes:** no problems of their own. Steps 5, 8 and 13 contradict the "restart is always required" line, as covered above.
