# Runbook: rotate the ingest service API key

Audience: the on-call engineer. Expected duration: 20 minutes. Perform during the daily quiet window (02:00 to 04:00 UTC) unless the key is known to be compromised, in which case perform immediately and follow the compromised-key variant where a step gives one.

## Layout

- Service host: `ingest-01.prod.internal` (SSH as `deploy`).
- Service unit: `ingest.service` (systemd).
- Config directory: `/etc/ingest/config/`. The live key file is `keys.yaml` in that directory, owned by `ingest:ingest`, mode 0600.
- Upstream key issuer: the Vendor Console at `https://console.vendor.example/keys`. You need the `ingest-rotator` role.
- Metrics: Grafana dashboard "Ingest / Health", panel "Consumer lag (s)".

## Before you start

1. Confirm you hold the `ingest-rotator` role: open the Vendor Console, Settings, Roles. If it is missing, stop and page the platform lead.
2. Open the Grafana dashboard and note the current consumer lag. Record it in the change ticket. If it is already above 8 seconds, stop and page the platform lead unless the key is compromised: the lag check in step 11 cannot distinguish a rotation problem from a pre-existing one.
3. Announce in `#ingest-ops`: "Starting ingest key rotation, ticket <id>."

## Rotation

4. In the Vendor Console, create a new key named `ingest-prod-YYYYMMDD` with the `read:feed` scope only. Copy the secret; it is shown once.
5. SSH to the service host and stop the service, then confirm it is stopped (expect `inactive`):
   ```
   sudo systemctl stop ingest.service
   systemctl is-active ingest.service
   ```
6. Back up the live key file so the old key can be restored in Rollback:
   ```
   sudo -u ingest cp -p /etc/ingest/config/keys.yaml /etc/ingest/config/keys.yaml.bak
   ```
7. Put the new key in a shell variable without echoing it or writing it to history (paste the secret at the prompt, then Enter):
   ```
   read -rs NEW_KEY
   ```
8. Write the new key into the live file, replacing the `api_key` value, then confirm the line was changed (expect `1`). If the secret contains `|`, `&` or `\`, edit the file with `sudo -u ingest -e /etc/ingest/config/keys.yaml` instead of `sed`:
   ```
   sudo -u ingest sed -i "s|^api_key: .*|api_key: $NEW_KEY|" /etc/ingest/config/keys.yaml
   sudo -u ingest grep -c "^api_key: $NEW_KEY\$" /etc/ingest/config/keys.yaml
   ```
9. Check the file parses:
   ```
   sudo -u ingest python3 -c "import yaml,sys; yaml.safe_load(open('/etc/ingest/config/keys.yaml'))" && echo OK
   ```
10. Start the service and verify it authenticated with the new key: `is-active` must print `active`, and the last 50 journal lines must contain no `401`, `403` or `auth` errors. If either check fails, go to Rollback.
   ```
   sudo systemctl start ingest.service
   systemctl is-active ingest.service
   journalctl -u ingest.service -n 50 --no-pager
   ```
11. Watch the Grafana lag panel. Wait until lag is at or below 8 seconds. If it has not got there within 15 minutes of step 10, go to Rollback.
12. If the key was compromised: in the Vendor Console delete the old key now. Rollback is no longer possible after this; a failure from here on is handled by paging the platform lead. Otherwise leave the old key in place and create a ticket to delete it after 24 hours of healthy operation (it stays valid for 24 hours and is the Rollback path).
13. Announce in `#ingest-ops`: "Ingest key rotation complete, ticket <id>."

## Rollback

If step 10 fails or lag does not recover within 15 minutes in step 11. Not available once the old key has been deleted (step 12, compromised case): skip to step 15.

14. Restore the previous key from the backup taken in step 6 and start the service:
   ```
   sudo systemctl stop ingest.service
   sudo -u ingest cp -p /etc/ingest/config/keys.yaml.bak /etc/ingest/config/keys.yaml
   sudo systemctl start ingest.service
   ```
15. Page the platform lead with the ticket id and the `journalctl -u ingest.service -n 200` output.

## Notes

- The service reads `keys.yaml` only at start, so a stop and start is always required. A `restart` while the file still holds the old key loads the old key and a later `start` is a no-op.
- The `read:feed` scope is deliberate; `write:feed` keys have been issued by mistake before and the vendor does not revoke scopes on an existing key.
- Lag normally sits between 2 and 8 seconds. The alert threshold is 60 seconds.
- `keys.yaml.bak` holds the old secret. Delete it when the old key is deleted.
