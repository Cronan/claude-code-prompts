# Runbook: rotate the ingest service API key

Audience: the on-call engineer. Expected duration: 30 minutes. Perform during the daily quiet window (02:00 to 04:00 UTC) unless the key is known to be compromised, in which case perform immediately.

## Layout

- Service host: `ingest-01.prod.internal` (SSH as `deploy`, which has sudo). Run every command below on this host.
- Service unit: `ingest.service` (systemd).
- Config directory: `/etc/ingest/config/`. The live key file is `keys.yaml` in that directory, owned by `ingest:ingest`, mode 0600. It contains one top-level line of the form `api_key: <secret>`.
- Upstream key issuer: the Vendor Console at `https://console.vendor.example/keys`. You need the `ingest-rotator` role.
- Metrics: Grafana dashboard "Ingest / Health", panel "Consumer lag (s)".

## Before you start

1. Raise a change ticket titled "Ingest key rotation" (if the key is compromised, use the incident ticket instead). Its id is `<id>` wherever this runbook says `<id>`.
2. Confirm you hold the `ingest-rotator` role: open the Vendor Console, Settings, Roles. If it is missing, stop and page the platform lead.
3. In the Vendor Console key list there must be exactly one `ingest-prod-*` key. Record its name in the ticket; it is the "old key" below. If there is more than one, stop and page the platform lead before changing anything.
4. Open the Grafana dashboard and note the current consumer lag. Record it in the ticket.
5. Announce in `#ingest-ops`: "Starting ingest key rotation, ticket <id>."

## Rotation

6. In the Vendor Console, create a new key named `ingest-prod-YYYYMMDD` (today's date, UTC) with the `read:feed` scope only. Copy the secret; it is shown once.
7. SSH to the service host and back up the live key file. It must print `OK`; if it does not, a backup from an earlier attempt exists: stop and page the platform lead.
   ```
   sudo test ! -e /etc/ingest/config/keys.yaml.bak && sudo cp -p /etc/ingest/config/keys.yaml /etc/ingest/config/keys.yaml.bak && echo OK
   ```
8. Put the new secret in a shell variable without echoing it: run `read -rs NEW_KEY`, paste the secret, press Enter. If your SSH session drops before step 10 completes, repeat this step.
9. Write the new key into the live file. The file is rewritten in place, so owner and mode are unchanged:
   ```
   sudo --preserve-env=NEW_KEY python3 -c "import os,re,pathlib; p=pathlib.Path('/etc/ingest/config/keys.yaml'); s=p.read_text(); n=re.sub(r'(?m)^api_key: .*$', lambda m: 'api_key: '+os.environ['NEW_KEY'], s, count=1); assert n!=s, 'api_key line not found'; p.write_text(n)"
   ```
10. Check the file parses with the new value and keeps its ownership and mode. Both lines must print `OK`; if either does not, go to Rollback. Then clear the variable:
    ```
    sudo --preserve-env=NEW_KEY python3 -c "import os,yaml; d=yaml.safe_load(open('/etc/ingest/config/keys.yaml')); assert d['api_key']==os.environ['NEW_KEY']" && echo OK
    test "$(sudo stat -c '%U:%G %a' /etc/ingest/config/keys.yaml)" = "ingest:ingest 600" && echo OK
    unset NEW_KEY
    ```
11. Restart the service. `is-active` must print `active` and the count must print `0`. If either fails, go to Rollback.
    ```
    sudo systemctl restart ingest.service && sleep 30 && systemctl is-active ingest.service
    sudo journalctl -u ingest.service --since "-1min" --no-pager | grep -ciE 'auth|401'
    ```
12. Watch the Grafana lag panel for up to 15 minutes. Continue once lag has stayed in the normal range (2 to 8 seconds) for 5 consecutive minutes. If lag crosses the 60-second alert threshold, or is not in range after 15 minutes, go to Rollback.
13. In the Vendor Console, delete the old key recorded in step 3. Do not delete the new key.
14. Remove the backup: `sudo rm /etc/ingest/config/keys.yaml.bak`.
15. Announce in `#ingest-ops`: "Ingest key rotation complete, ticket <id>."

## Rollback

Use this if step 10, 11 or 12 fails. Rollback is only possible before step 13. If the old key is compromised, do not restore it: delete it in the Vendor Console as in step 13, run `sudo systemctl stop ingest.service`, and skip to step 18. If step 13 has already run, skip to step 18.

16. Restore the backup and restart the service, then repeat the checks in step 11 and the lag watch in step 12. If either fails again, go to step 18.
    ```
    sudo cp -p /etc/ingest/config/keys.yaml.bak /etc/ingest/config/keys.yaml && sudo rm /etc/ingest/config/keys.yaml.bak
    sudo systemctl restart ingest.service
    ```
17. In the Vendor Console, delete the new key created in step 6. This also frees the name for a retry.
18. Page the platform lead with the ticket id and the output of `sudo journalctl -u ingest.service -n 200 --no-pager` from the service host.

## Notes

- The service reads `keys.yaml` only at start, so a restart is always required.
- The `read:feed` scope is deliberate; `write:feed` keys have been issued by mistake before and the vendor does not revoke scopes on an existing key.
- Lag normally sits between 2 and 8 seconds. The alert threshold is 60 seconds.
