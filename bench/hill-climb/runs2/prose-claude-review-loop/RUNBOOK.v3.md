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
6. Back up the live key file so the old key can be restored in Rollback. If the backup already exists, a previous attempt was interrupted: stop and page the platform lead rather than overwrite it.
   ```
   sudo -u ingest test ! -e /etc/ingest/config/keys.yaml.bak && sudo -u ingest cp -p /etc/ingest/config/keys.yaml /etc/ingest/config/keys.yaml.bak && echo OK
   ```
7. Put the new key in a shell variable without echoing it or writing it to history (paste the secret at the prompt, then Enter):
   ```
   read -rs NEW_KEY
   ```
8. Write the new key into the live file, replacing the `api_key` value. The key is passed on stdin so it never appears in the sudo log or `ps`. The command prints the number of lines replaced; expect `1`. If it prints anything else, go to Rollback.
   ```
   printf '%s' "$NEW_KEY" | sudo -u ingest python3 -c "import re,sys; p='/etc/ingest/config/keys.yaml'; k=sys.stdin.read(); s=open(p).read(); n,c=re.subn(r'(?m)^api_key: .*$', lambda m: 'api_key: '+k, s); open(p,'w').write(n); print(c)"; unset NEW_KEY
   ```
9. Check the file parses. If it does not print `OK`, go to Rollback.
   ```
   sudo -u ingest python3 -c "import yaml,sys; yaml.safe_load(open('/etc/ingest/config/keys.yaml'))" && echo OK
   ```
10. Start the service, wait 30 seconds for it to make its first upstream call, then verify: `is-active` must print `active`, and the journal since the start must contain no `401`, `403` or authentication failure lines (the grep must print nothing). If either check fails, go to Rollback.
   ```
   sudo systemctl start ingest.service; sleep 30
   systemctl is-active ingest.service
   journalctl -u ingest.service --since "-1min" --no-pager | grep -Ei '401|403|auth[a-z]* *(fail|error)'
   ```
11. Watch the Grafana lag panel. Wait until lag is at or below 8 seconds. If it has not got there within 15 minutes of step 10, go to Rollback.
12. If the key was compromised: in the Vendor Console delete the old key now and run `sudo rm /etc/ingest/config/keys.yaml.bak`. Rollback is no longer possible after this; a failure from here on is handled by paging the platform lead. Otherwise leave the old key in place and create a ticket to delete it, and to run that `rm`, after 24 hours of healthy operation (it stays valid for 24 hours and is the Rollback path).
13. Announce in `#ingest-ops`: "Ingest key rotation complete, ticket <id>."

## Rollback

If any check in steps 8 to 11 fails. Not available once the old key has been deleted (step 12, compromised case): skip to step 15.

14. Restore the previous key from the backup taken in step 6, start the service, and verify as in step 10: `is-active` prints `active`, the grep prints nothing, and lag is at or below 8 seconds within 15 minutes. If all three pass, the service is back on the old key; go to step 15 anyway so the lead knows the rotation did not take. If any fails, go to step 15 at once.
   ```
   sudo systemctl stop ingest.service
   sudo -u ingest cp -p /etc/ingest/config/keys.yaml.bak /etc/ingest/config/keys.yaml
   sudo systemctl start ingest.service; sleep 30
   systemctl is-active ingest.service
   journalctl -u ingest.service --since "-1min" --no-pager | grep -Ei '401|403|auth[a-z]* *(fail|error)'
   ```
15. Page the platform lead with the ticket id, whether the service is up, and the `journalctl -u ingest.service -n 200` output.

## Notes

- The service reads `keys.yaml` only at start, so a stop and start is always required. A `restart` while the file still holds the old key loads the old key and a later `start` is a no-op.
- The `read:feed` scope is deliberate; `write:feed` keys have been issued by mistake before and the vendor does not revoke scopes on an existing key.
- Lag normally sits between 2 and 8 seconds. The alert threshold is 60 seconds.
- `keys.yaml.bak` holds the old secret. It is removed in step 12 or by the follow-up ticket; its presence at step 6 means a previous run did not finish.
