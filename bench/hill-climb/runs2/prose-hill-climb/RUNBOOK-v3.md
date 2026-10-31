# Runbook: rotate the ingest service API key

Audience: the on-call engineer. Expected duration: 20 minutes. Perform during the daily quiet window (02:00 to 04:00 UTC) unless the key is known to be compromised, in which case perform immediately.

## Layout

- Service host: `ingest-01.prod.internal` (SSH as `deploy`).
- Service unit: `ingest.service` (systemd).
- Config directory: `/etc/ingest/config/`. The live key file is `keys.yaml` in that directory, owned by `ingest:ingest`, mode 0600.
- Upstream key issuer: the Vendor Console at `https://console.vendor.example/keys`. You need the `ingest-rotator` role.
- Metrics: Grafana dashboard "Ingest / Health", panel "Consumer lag (s)".

## Before you start

1. Confirm you hold the `ingest-rotator` role: open the Vendor Console, Settings, Roles. If it is missing, stop and page the platform lead.
2. Open the Grafana dashboard and note the current consumer lag. Record it in the change ticket.
3. Announce in `#ingest-ops`: "Starting ingest key rotation, ticket <id>."

## Rotation

4. In the Vendor Console, create a new key named `ingest-prod-YYYYMMDD` with the `read:feed` scope only. Copy the secret; it is shown once.
5. SSH to the service host and stop the service:
   ```
   sudo systemctl stop ingest.service
   ```
6. Back up the live file, then write the new key into it, replacing the `api_key` value. At the `read` prompt paste the secret from step 4 and press Enter (nothing is echoed):
   ```
   sudo -u ingest cp -p /etc/ingest/config/keys.yaml /etc/ingest/config/keys.yaml.bak
   read -rs NEW_KEY
   sudo -u ingest sed -i "s|^api_key: .*|api_key: $NEW_KEY|" /etc/ingest/config/keys.yaml
   ```
7. Check the file parses and holds exactly the new key:
   ```
   sudo -u ingest python3 -c "import yaml,sys; yaml.safe_load(open('/etc/ingest/config/keys.yaml'))" && sudo -u ingest grep -qxF "api_key: $NEW_KEY" /etc/ingest/config/keys.yaml && echo OK
   ```
   If `OK` is not printed, go to step 13.
8. Start the service and note the time; the 15-minute rollback clock starts now:
   ```
   sudo systemctl start ingest.service
   ```
9. Verify the rotation worked: both commands must pass. If either fails, go to step 13.
   ```
   systemctl is-active ingest.service
   sudo journalctl -p err -u ingest.service --since "-5min" --no-pager
   ```
   The first prints `active`; the second prints no log lines (a "No entries" or "-- No entries --" line alone is a pass).
10. Watch the Grafana lag panel. Continue when lag is 8 seconds or below (the top of the normal range in Notes). If it is still above 8 seconds 15 minutes after step 8, go to step 13.
11. In the Vendor Console, delete the old key (the `ingest-prod-*` key with the earlier date) so it cannot be used. Rollback is no longer available after this step.
12. Announce in `#ingest-ops`: "Ingest key rotation complete, ticket <id>."

## Rollback

Use this section if step 7 does not print `OK`, step 9 fails, or lag is still above 8 seconds 15 minutes after step 8. It applies only before step 11; once the old key is deleted, treat any failure as a new incident and page the platform lead.

13. Restore the previous key: the old key stays valid for 24 hours after rotation, so put the backup from step 6 back in place and restart the service, then repeat the step 9 checks:
   ```
   sudo -u ingest cp -p /etc/ingest/config/keys.yaml.bak /etc/ingest/config/keys.yaml
   sudo systemctl restart ingest.service
   ```
14. In the Vendor Console, delete the new key created in step 4. Announce in `#ingest-ops`: "Ingest key rotation rolled back, ticket <id>."
15. Page the platform lead with the ticket id, whether the step 9 checks passed after the restore, and the `journalctl -u ingest.service -n 200` output.

## Notes

- The service reads `keys.yaml` only at start, so a restart is always required.
- The `read:feed` scope is deliberate; `write:feed` keys have been issued by mistake before and the vendor does not revoke scopes on an existing key.
- Lag normally sits between 2 and 8 seconds. The alert threshold is 60 seconds.
