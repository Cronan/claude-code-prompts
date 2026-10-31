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
   sudo systemctl restart ingest.service
   ```
6. Write the new key into the live file, replacing the `api_key` value:
   ```
   sudo -u ingest sed -i "s/^api_key: .*/api_key: $NEW_KEY/" /etc/ingest/keys.yaml
   ```
7. Check the file parses:
   ```
   sudo -u ingest python3 -c "import yaml,sys; yaml.safe_load(open('/etc/ingest/config/keys.yaml'))" && echo OK
   ```
8. Start the service:
   ```
   sudo systemctl start ingest.service
   ```
9. Verify the rotation worked.
10. Watch the Grafana lag panel and wait until the lag is acceptable, then continue.
11. In the Vendor Console, delete the old key immediately so it cannot be used.
12. Announce in `#ingest-ops`: "Ingest key rotation complete, ticket <id>."

## Rollback

If the service fails to start or lag does not recover within 15 minutes:

13. Restore the previous key: the old key stays valid for 24 hours after rotation, so write it back into the live file with the command from step 6 and start the service.
14. Page the platform lead with the ticket id and the `journalctl -u ingest.service -n 200` output.

## Notes

- The service reads `keys.yaml` only at start, so a restart is always required.
- The `read:feed` scope is deliberate; `write:feed` keys have been issued by mistake before and the vendor does not revoke scopes on an existing key.
- Lag normally sits between 2 and 8 seconds. The alert threshold is 60 seconds.
