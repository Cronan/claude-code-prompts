# Review loop report: RUNBOOK.md

Skill: claude-review-loop (max 3 iterations). Artefact: /home/claude/bench/runs2/prose-claude-review-loop/RUNBOOK.md (branch `master`, one commit; "diff against main" taken as the whole file). Final runbook left uncommitted in the working tree; versioned copies RUNBOOK.v2.md, v3.md, v4.md beside it.

## Stopping rule

The 3-iteration cap. Round 3 still produced four Fix items, which were applied, but the skill allows no fourth re-review, so the round 3 changes are unreviewed.

## Adaptations

- Reviewer could not run `git diff main...HEAD` (no `main`, Bash disallowed); it was told to Read RUNBOOK.md as the whole diff.
- Step 4 of the skill (`npm run lint`, `npm run test`): no lint or test command exists, so skipped. In its place the three frozen mechanical checks were run after every round: under 80 lines (54 -> 71 -> 72 -> 73), section order Layout, Before you start, Rotation, Rollback, Notes unchanged, steps numbered 1 to 15 continuously. All pass. The shell and Python one-liners introduced were also executed locally against a dummy keys.yaml.
- Re-review rounds were told which lines were unchanged and which skipped items not to re-raise.

## Reviewer processes

Three, all `claude -p --no-session-persistence --permission-mode default --model sonnet --disallowedTools Bash,Edit,Write`. Reports verbatim in reports/round{1,2,3}-reviewer.md; triage tables in reports/round{1,2,3}-fixlist.md.

## Findings per round

Round 1: 8 findings, 8 Fix, 0 Skip. Step 5 ran `restart` instead of `stop`; sed path /etc/ingest/keys.yaml vs live /etc/ingest/config/keys.yaml; $NEW_KEY never set and stripped by sudo; old key never backed up so rollback impossible; "verify the rotation worked" had no command; "acceptable" lag undefined; old key deleted immediately, contradicting the 24 h rollback window; compromised-key case left the old key usable for 24 h.

Round 2: 7 findings, 6 Fix, 1 Skip. Fixed: secret on the sudo command line (sudo log, ps); no failure path if the write or parse check failed with the service down; journalctl -n 50 read stale lines and bare `auth` matched benign text; rollback never verified the service came back; cp -p overwrote an existing .bak on re-run; .bak deletion stated in Notes but performed nowhere. Skipped: deleting the new vendor key after rollback (hygiene, not a defect that blocks or misleads the engineer).

Round 3: 4 findings, 4 Fix, 0 Skip. Backup-exists guard blocked a compromised rotation while a legitimate .bak from a finished rotation sat on disk; backup chain silent on collision; bare `401|403` matched PIDs and ports; `--since -1min` not tied to the service start.

## What changed

- Step 5: `stop` plus `is-active` check.
- Step 6 (new): ticket-stamped backup `keys.yaml.bak.$TICKET`, explicit EXISTS/OK output, stop on EXISTS.
- Step 7 (new): `read -rs NEW_KEY`.
- Step 8: Python replacement reading the key from stdin (handles /, &, \, | in the secret; prints replacement count), `unset NEW_KEY`; correct path.
- Steps 8, 9: explicit "go to Rollback" on failure.
- Step 10: timestamp before start, 30 s wait, `is-active`, anchored journal grep.
- Step 11: lag <= 8 s within 15 min, else Rollback.
- Step 12: compromised branch deletes old key and backup now; otherwise 24 h soak ticket.
- Step 2: stop if lag already above 8 s (non-compromised).
- Rollback: trigger widened to steps 8 to 11; restore from backup, verify as step 10, remove backup, always page.
- Notes: restart/no-op explanation; backup lifecycle.

Also fixed by me outside reviewer findings: the round 3 step 6 chain as first written printed both EXISTS and OK on collision (&&/|| precedence); replaced with an if/else and tested. The round 2 Python replacement as first written would have mangled a backslash in the secret; switched to a lambda replacement and tested.

## What remains

- Round 3 changes have not been re-reviewed (cap reached).
- Step 10's log check is a guess at the service's wording for auth failures; the real log line is unknown and should be confirmed by someone with access to the service logs. The 30 s wait is likewise an assumption about when the first upstream call happens.
- Skipped: deleting the new vendor key after a rollback.
- Step 14 relies on `$B` surviving in the shell, with a fallback path given; `TICKET=<id>` must be typed by the engineer.
- Nothing committed; `git status` shows RUNBOOK.md modified and three untracked versioned copies.
