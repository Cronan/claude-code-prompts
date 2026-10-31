Seeded defects in RUNBOOK.md (hidden from contenders):
P1 Step 5 says "stop the service" but the command is `systemctl restart`. Blocking: wrong action.
P2 Step 6 writes to `/etc/ingest/keys.yaml`; the layout and step 7 say `/etc/ingest/config/keys.yaml`. Blocking: wrong path.
P3 Step 6 uses `$NEW_KEY`, never defined; step 4 only says "copy the secret". Blocking: cannot execute without guessing.
P4 Step 9 "Verify the rotation worked" has no command or expected output. Blocking: cannot take the step.
P5 Step 10 "until the lag is acceptable" is undefined; Notes give 2 to 8 s normal and 60 s alert, so a number exists. Misleading/blocking: undefined quantity.
P6 Step 11 deletes the old key immediately; rollback step 13 relies on the old key staying valid for 24 hours. Blocking: contradiction that breaks rollback.
Intended and correct: quiet-window rule, role check, sed as ingest user, yaml parse check, read:feed scope note, 15-minute rollback trigger, journalctl line.
Frozen: section order (Layout, Before, Rotation, Rollback, Notes), step numbering continuous, under 80 lines, no new sections.
