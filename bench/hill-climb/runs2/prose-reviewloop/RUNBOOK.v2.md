# Runbook: rotate the ingest service API key

Audience: the on-call engineer. Expected duration: 30 minutes. Perform during the daily quiet window (02:00 to 04:00 UTC) unless the key is known to be compromised, in which case perform immediately.

## Layout

- Service host: `ingest-01.prod.internal` (SSH as `deploy`).
- Service unit: `ingest.service` (systemd).
- Config directory: `/etc/ingest/config/`. The live key file is `keys.yaml` in that directory, owned by `ingest:ingest`, mode 0600. It contains one top-level line of the form `api_key: <secret>`.
- Upstream key issuer: the Vendor Console at `https://console.vendor.example/keys`. You need the `ingest-rotator` role.
- Metrics: Grafana dashboard "Ingest / Health", panel "Consumer lag (s)". Normal lag is 2 to 8 seconds.

## Before you start

1. Raise a change ticket titled "Ingest key rotation" (if the key is compromised, use the incident ticket instead). Its id is `<id>` wherever this runbook says `<id>`.
2. Confirm you hold the `ingest-rotator` role: open the Vendor Console, Settings, Roles. If it is missing, stop and page the platform lead.
3. In the Vendor Console key list, record in the ticket the name of the current `ingest-prod-*` key. This is the "old key" below.
4. Open the Grafana dashboard and note the current consumer lag. Record it in the ticket.
5. Announce in `#ingest-ops`: "Starting ingest key rotation, ticket <id>."

## Rotation

6. In the Vendor Console, create a new key named `ingest-prod-YYYYMMDD` (today's date, UTC) with the `read:feed` scope only. Copy the secret; it is shown once.
7. SSH to the service host and stop the service:
   ```
   sudo systemctl stop ingest.service
   ```
8. Back up the live key file (this is what Rollback restores):
   ```
   sudo cp -p /etc/ingest/config/keys.yaml /etc/ingest/config/keys.yaml.bak
   ```
9. Put the new secret in a shell variable without echoing it: run `read -rs NEW_KEY`, paste the secret, press Enter.
10. Write the new key into the live file, replacing the `api_key` value:
    ```
    sudo -u ingest sed -i "s|^api_key: .*|api_key: $NEW_KEY|" /etc/ingest/config/keys.yaml
    ```
11. Check the new value is in place and the file parses. Both commands must print `OK`:
    ```
    sudo -u ingest grep -qxF "api_key: $NEW_KEY" /etc/ingest/config/keys.yaml && echo OK
    sudo -u ingest python3 -c "import yaml; yaml.safe_load(open('/etc/ingest/config/keys.yaml'))" && echo OK
    ```
12. Start the service and confirm it is running. `is-active` must print `active`; the log tail must show no `authentication` or `401` lines:
    ```
    sudo systemctl start ingest.service && sleep 10 && systemctl is-active ingest.service
    sudo journalctl -u ingest.service -n 50 --no-pager
    ```
13. Watch the Grafana lag panel for up to 15 minutes. Continue once lag is back in the normal range (2 to 8 seconds). If it is not there after 15 minutes, go to Rollback.
14. In the Vendor Console, delete the old key recorded in step 3. Do not delete the new key.
15. Announce in `#ingest-ops`: "Ingest key rotation complete, ticket <id>."

## Rollback

Use this if step 12 does not print `active` or step 13 times out. Rollback is only possible before step 14; once the old key is deleted, skip to step 17. If the old key is compromised, do not restore it: leave the service stopped and skip to step 17.

16. Restore the backup and restart the service, then repeat the checks in step 12:
    ```
    sudo cp -p /etc/ingest/config/keys.yaml.bak /etc/ingest/config/keys.yaml
    sudo systemctl restart ingest.service
    ```
17. Page the platform lead with the ticket id and the output of `sudo journalctl -u ingest.service -n 200 --no-pager` from the service host.

## Notes

- The service reads `keys.yaml` only at start, so a stop/start or restart is always required.
- The `read:feed` scope is deliberate; `write:feed` keys have been issued by mistake before and the vendor does not revoke scopes on an existing key.
- Lag normally sits between 2 and 8 seconds. The alert threshold is 60 seconds.
- Once the rotation is complete, remove the backup: `sudo rm /etc/ingest/config/keys.yaml.bak`.
