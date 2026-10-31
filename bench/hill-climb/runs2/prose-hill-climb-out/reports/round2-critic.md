**4 blocking, 3 misleading, 5 minor**

**Layout**
- **Minor.** Line 9 says who owns `keys.yaml` (`ingest:ingest`, 0600) but not who owns the directory. Step 6's `cp` to `keys.yaml.bak` and `sed -i` both create new files in `/etc/ingest/config/`, so they fail if `ingest` can't write there. The service is already stopped by then. Fix: state the directory's owner and mode, or run those two commands as root.

**Before you start**
- **Blocking.** Step 2, "Record it in the change ticket", and step 3, "ticket <id>": nothing says where the ticket comes from or whether to create one, so neither step can be done. Fix: "Open a change ticket in <system> (or use the ticket on the page) and use its id below."
- **Blocking.** Step 2, "Open the Grafana dashboard": no Grafana URL is given anywhere, while the Vendor Console gets a full URL. Fix: add the dashboard URL to Layout line 11.
- **Minor.** Step 2's baseline lag is recorded but no later step uses it. Fix: refer to it in step 10, or drop it.

**Rotation**
- **Blocking.** Step 7, "&& echo OK": nothing says what to do if `OK` doesn't print. The service is stopped at that point, and the rollback trigger only covers start failure and lag. This will happen if the secret contains `|`, `&` or `\`, because step 6's `sed` will mangle it or error out. Fix: "If OK is not printed, go to step 13."
- **Blocking.** Step 9, "Verify the rotation worked.": the step has no command and no expected result. Fix: give a concrete check, e.g. `systemctl is-active ingest.service` returns `active` and the journal shows no auth errors since the start.
- **Blocking.** Step 10, "wait until the lag is acceptable", and line 47, "lag does not recover within 15 minutes": neither "acceptable" nor "recover" has a number. Notes gives two candidates (2–8 s normal, 60 s alert). The 15 minutes also has no start point. Fix: "Continue when lag ≤ 8 s; if it is still above 8 s 15 minutes after step 8, go to step 13."
- **Misleading.** Step 11, "(OWNER TO SET: the window …)": the placeholder was never filled in. Nobody is assigned to the later deletion and no time is given, so the old key will just sit there. Fix: replace it with a concrete window and an owner, e.g. "the on-call engineer deletes it after 4 h; add a ticket reminder."
- **Minor.** Step 11, "record the name of the old key": it doesn't say how to pick out the old key if the console lists several. Fix: "the key currently named `ingest-prod-<previous date>` with `read:feed` scope."
- **Minor.** Steps 6–7 rely on `$NEW_KEY`. If you run step 7 in a new SSH session, the variable is empty and the check fails for no real reason. Fix: "Run steps 6–7 in the same shell, then `unset NEW_KEY`."
- **Minor.** Step 6's `sed` line puts the secret in `sed`'s command-line arguments, where other users on the host can see it in `ps`. Fix: build the new file from stdin, or with `envsubst`, instead of passing the key as an argument.
- **Minor.** Step 4, "Copy the secret; it is shown once": it doesn't say where to keep the secret until step 6. Fix: name the approved temporary store (e.g. the password manager).

**Rollback**
- **Misleading.** Line 47's trigger list doesn't include a failed step 7. Step 13 then doesn't check that rollback worked, doesn't announce it in `#ingest-ops`, and leaves the new key active in the Vendor Console. Fix: add "rotation step fails" to the triggers, rerun the step 9 check, announce the rollback, and revoke the new key.
- **Misleading.** Line 47's 15-minute lag trigger means step 13 can still be reached after step 11 has deleted a compromised old key. Step 13 then restores a dead key and the service stays down. Fix: "If the old key was deleted at step 11, skip step 13 and page the platform lead immediately."

**Notes**
- Fine. Its only problem is that steps 10 and 47 don't refer to its thresholds, which is covered above.
