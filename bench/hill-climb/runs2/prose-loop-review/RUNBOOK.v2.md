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

4. In the Vendor Console, create a new key named `ingest-prod-YYYYMMDD` (today's date, UTC) with the `read:feed` scope only. Copy the secret; it is shown once. Note the name of the existing old key, you delete it in step 11.
5. SSH to the service host and stop the service. The second command must print `inactive`:
   ```
   sudo systemctl stop ingest.service
   systemctl is-active ingest.service
   ```
6. Back up the live file, then write the new key into it. At the `read` prompt paste the secret from step 4 and press Enter (nothing is echoed):
   ```
   sudo -u ingest cp -p /etc/ingest/config/keys.yaml /etc/ingest/config/keys.yaml.bak
   read -rs NEW_KEY
   ESC=$(printf '%s' "$NEW_KEY" | sed 's/[&|\\]/\\&/g')
   sudo -u ingest sed -i "s|^api_key: .*|api_key: $ESC|" /etc/ingest/config/keys.yaml
   ```
7. Check the file parses and holds the new key. Expected output is `OK` then `1`; anything else (an error, `0`, or an "empty" message) means step 6 failed, so go to Rollback:
   ```
   sudo -u ingest python3 -c "import yaml,sys; yaml.safe_load(open('/etc/ingest/config/keys.yaml'))" && echo OK
   sudo -u ingest grep -cFx "api_key: ${NEW_KEY:?empty}" /etc/ingest/config/keys.yaml
   ```
8. Start the service and note the time:
   ```
   sudo systemctl start ingest.service
   ```
9. Verify the service is up and not logging errors. The first command must print `active`; the second must print no log lines:
   ```
   systemctl is-active ingest.service
   sudo journalctl -u ingest.service --since "2 min ago" -p err --no-pager
   ```
10. In Grafana, watch "Consumer lag (s)". Continue when lag has stayed at or below 8 s for 5 consecutive minutes. If that has not happened 15 minutes after step 8, go to Rollback.
11. In the Vendor Console, delete the old key noted in step 4. Then remove the backup on the host: `sudo -u ingest rm /etc/ingest/config/keys.yaml.bak`.
12. Announce in `#ingest-ops`: "Ingest key rotation complete, ticket <id>."

## Rollback

Use this if step 7 fails, step 9 fails, or step 10's lag condition is not met 15 minutes after step 8. It restores the old key, so do not use it if the old key is known to be compromised: skip to step 14 instead.

13. Restore the backup taken in step 6 and start the service, then repeat step 9:
   ```
   sudo systemctl stop ingest.service
   sudo -u ingest cp -p /etc/ingest/config/keys.yaml.bak /etc/ingest/config/keys.yaml
   sudo systemctl start ingest.service
   ```
14. Page the platform lead with the ticket id. On `ingest-01.prod.internal` run `sudo journalctl -u ingest.service -n 200 --no-pager` and paste the output into the change ticket.

## Notes

- The service reads `keys.yaml` only at start, so a restart is always required.
- The `read:feed` scope is deliberate; `write:feed` keys have been issued by mistake before and the vendor does not revoke scopes on an existing key.
- Lag normally sits between 2 and 8 seconds. The alert threshold is 60 seconds.
