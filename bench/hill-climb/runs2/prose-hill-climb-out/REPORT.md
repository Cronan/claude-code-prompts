# Hill-climb report: ingest key rotation runbook

Artefact: `/home/claude/bench/runs2/prose-hill-climb/RUNBOOK.md` (git, one commit `a29dc6a` on `master`). Skill: `/home/claude/bench/skills/hill-climb.md`. Delivered version: v3, in place at `RUNBOOK.md` (uncommitted working-tree change; `RUNBOOK-v2.md` and `RUNBOOK-v3.md` beside it, untracked). No branch created, nothing pushed.

## Resumption

The agent running this climb stopped at about 15:45 UTC on 2026-10-31, after writing `reports/round3-fixlist.md` and copying `RUNBOOK-v3.md` over `RUNBOOK.md`. Everything up to and including the round-3 fix decision was complete; only this report was missing. A second agent resumed at about 16:44 UTC. It ran no further critic or verifier processes. It re-read the brief, the skill, all nine reports and the three versions, re-ran the mechanical verifier on `RUNBOOK.md`, confirmed `RUNBOOK.md` is byte-identical to `RUNBOOK-v3.md`, confirmed the round-3 fix decision was correct under the skill's final-call rule, and wrote this report. No `RUNBOOK-v4.md` exists because no round-3 batch was applied (see "Round 3" below).

## Contract (Step 0)

- Objective: an on-call engineer with no other context can execute the runbook without asking the author a question.
- Frozen: under 80 lines; section order Layout, Before you start, Rotation, Rollback, Notes; step numbering continuous. Also the house structure (numbered steps with fenced commands).
- Verifiers: the three mechanical checks only, run as `python3 -I verify.py RUNBOOK-vN.md` (script in the session scratchpad; checks line count < 80, exact section order, numbering 1..N). None covers correctness, so the climb was judgement-only for correctness.
- Stopping rules: 1 cannot fire (no correctness verifier); 2 and 3 live; cap 3 critic calls (prose figure, as the brief instructed).

## Adaptations of the skill to this session

- No Agent tool. Each critic and verifier was a fresh process: `claude -p --no-session-persistence --model <model> --disallowedTools Bash,Edit,Write -- "<prompt>"`, as the brief specified, run from the repo directory. The first round-1 critic attempt could not read the file (permission denied) and returned no findings; `--allowedTools Read` was added and the critic re-run. All later processes used the same form. Each critic got only the file path, intent, frozen behaviour, the executable-document ranking row and the walk-through persona (on-call engineer at 02:10 UTC). Each verifier got the file path, frozen behaviour, the ranking row and the numbered list of blocking and misleading claims.
- "Diff against main" is the whole file; critics were told not to read git history or any other file.
- Critic model: `opus`; verifier model: `sonnet`; fixer and orchestrator: `claude-fable-5-1`. All are the same model family as the fixer, so the skill's cross-family preference could not be met in this session. User memory does not describe the runbook's subject, so the critics were not primed.
- Final-call parallel critics: the skill defaults to two parallel critics on the final call, but two calls would have counted as calls 3 and 4 against a cap of 3, so round 3 ran a single critic.

## Reviewer processes

| # | Round | Role | Model | Report |
|---|---|---|---|---|
| 1 | 1 | critic | opus | aborted: could not read the file, no findings (not saved as a report) |
| 2 | 1 | critic | opus | `reports/round1-critic.md` |
| 3 | 1 | verifier | sonnet | `reports/round1-verifier.md` |
| 4 | 2 | critic | opus | `reports/round2-critic.md` |
| 5 | 2 | verifier | sonnet | `reports/round2-verifier.md` |
| 6 | 3 | critic | opus | `reports/round3-critic.md` |
| 7 | 3 | verifier | sonnet | `reports/round3-verifier.md` |

Seven processes launched; three critic calls counted against the cap; three verifier calls (not counted).

## Trajectory

Counts are confirmed findings after verification (the verifier's rank stands). Minor includes items the critic ranked higher and the verifier confirmed at minor. The critic's own raw tallies are in brackets.

| Round | Reviewed | Critic | Blocking | Misleading | Minor | Disputed |
|---|---|---|---|---|---|---|
| 1 | v1 (`a29dc6a`) | opus | 1 (5) | 7 (6) | 6 (3) | 0 |
| 2 | v2 | opus | 1 (4) | 5 (3) | 7 (5) | 0 |
| 3 | v3 | opus | 0 (1) | 3 (5) | 6 (5) | 2 |

Mechanical verifier passed on v1, v2, v3 and the delivered `RUNBOOK.md` (67 lines, section order intact, steps 1..15).

## What changed per round

Round 1 (v1 to v2, 8 fixes, `reports/round1-fixlist.md`): step 5 command changed from `restart` to `stop`; step 6 path corrected to `/etc/ingest/config/keys.yaml`, backup to `keys.yaml.bak` added, `read -rs NEW_KEY` added, sed delimiter changed to `|`; step 7 now also asserts the file holds exactly the new key; step 11 no longer deletes the old key during the run (placeholder for the deletion window, because when to delete was a policy question); step 13 restores from the backup and uses `restart` instead of `start`.

Round 2 (v2 to v3, 6 fixes, `reports/round2-fixlist.md`): step 7 gains "if OK is not printed, go to step 13"; step 8 starts the 15-minute rollback clock; step 9 replaced with two concrete checks (`systemctl is-active`, `journalctl -p err --since -5min`) and a pass condition; step 10 given the 8 s threshold from Notes and the 15-minute limit; step 11 placeholder removed, old key deleted in step 11 once step 10 has passed, with "rollback is no longer available after this step"; Rollback intro lists all three triggers and is scoped to before step 11; step 13 repeats the step 9 checks; new step 14 deletes the new key and announces the rollback; step 15 (was 14) pages with the re-check result.

Round 3: final critic call. No batch applied; see below.

## Stopping rule

Rule 4, the cap: three critic calls for prose. Rule 3 did not fire because round 2 had one confirmed blocking item, so there were not two consecutive zero-blocking reads. Rule 2 did not fire because round 3's confirmed misleading items (sed quoting, journal windows) are things the author could fix, not owner-only facts. Rule 1 cannot fire with no correctness verifier.

## Round 3: why no batch was applied

The skill applies findings from the final critic call only where a verifier covers the edit. The only verifiers here are the line count, section order and numbering checks. They can show that an edit did not break the structure; they cannot show that a changed `sed` or `journalctl` command is correct, which is what each round-3 fix would change. So none of the three confirmed misleading items is covered, none was applied, and all go to the owner's list. The same rule applies to the minors deferred from rounds 1 and 2. The delivered version is therefore v3, the version the round-3 critic read in full.

## Owner's list

Confirmed misleading in the final read, not applied:

1. Rotation, step 6, `sed -i "s|^api_key: .*|api_key: $NEW_KEY|"`. A secret containing `|`, `&` or `\` breaks or corrupts the substitution; a secret with YAML-significant characters (`#`, `: `, leading `*` or `&`) parses to a different value, and step 7's checks pass it. Conditional on the vendor's secret alphabet, which the runbook does not state. Fix: state the alphabet, or write the line with a quoting tool (for example a Python one-liner that dumps YAML).
2. Rotation, step 9, `--since "-5min"`. The window can include shutdown errors from step 5 (false failure) and the check runs immediately after start, before auth errors appear (false pass). Fix: `--since` the time noted in step 8, run 60 s after start.
3. Rollback, step 13, "repeat the step 9 checks". After a step 9 or step 10 trigger, the 5-minute window still holds the failed new-key run's errors, so the re-check fails even when the restore worked and step 15 reports it wrong. Fix: `--since` the step 13 restart time.

Disputed (critic claimed, verifier did not confirm):

4. Step 11 identifies the old key as "the `ingest-prod-*` key with the earlier date"; the critic said this assumes two keys and the naming pattern. The verifier held that step 4's naming makes the pattern safe. Owner to confirm the console only ever holds keys of that pattern.
5. Step 7 assumes PyYAML is installed on the host. The verifier held that a failed import sends you safely to rollback with the service stopped. Owner to confirm or add a pre-check.

Confirmed at minor, unfixed (no verifier covers them):

6. Steps 2, 3, 12, 14: the change ticket system and the source of `<id>` are never named (raised in all three rounds; critic ranked it blocking each time, verifier confirmed at minor each time). Suggested: "Create a change ticket in <system> (or use the page's incident id); use its id below."
7. Layout: no Grafana URL, only dashboard and panel names.
8. Layout: owner and mode of `/etc/ingest/config/` are not stated; step 6's `cp` and `sed -i` need `ingest` to be able to write there.
9. Step 2: the baseline lag is recorded but never used later.
10. Step 4: `YYYYMMDD` does not say UTC or local date, and at 02:10 UTC they can differ.
11. Step 4: where to keep the secret between steps 4 and 6 is not named.
12. Steps 6 and 7: `$NEW_KEY` must be set in the same shell; nothing says so or says to `unset` it afterwards; the secret appears in `sed`'s argument list (visible in `ps`).
13. Step 8: "note the time" does not say where (the ticket).
14. Step 10: a single reading at or below 8 s lets you continue while lag is still falling; a settled-for-N-minutes condition would be safer.
15. Step 11: `keys.yaml.bak` keeps the old secret after the old key is deleted; a cleanup step is missing.
16. Step 13: "the old key stays valid for 24 hours after rotation" sits oddly beside step 11 (the key is deleted there); "until deleted in step 11" is the accurate phrasing.
17. Step 15: `journalctl -u ingest.service -n 200` lacks `sudo`, while step 9 has it; as `deploy` it may show nothing.
18. Before you start: no pre-check that SSH as `deploy`, `sudo -u ingest` and writing to the config directory all work before a one-time secret is issued.

Policy decision taken in the climb that the owner should confirm:

19. Round 1 turned "delete the old key immediately" into a placeholder because the deletion window was a policy question. Round 2 removed the placeholder and restored deletion in step 11, after step 10 has passed, on the reasoning that rollback is only reachable before step 11 so the 24-hour validity no longer matters. That is a decision about the rollback window; if the owner wants a longer window (for example, to roll back a failure discovered hours later), step 11 and the Rollback scope sentence both change.

Assumptions the runbook makes that no cold reader could check:

20. The vendor keeps the old key valid for 24 hours after a new one is issued.
21. The service reads `keys.yaml` only at start.
22. `deploy` can `sudo systemctl` and `sudo -u ingest`; `ingest` can write to `/etc/ingest/config/`; `python3` with PyYAML is on the host.
23. The 8 s threshold and 15-minute limit were taken from the Notes and the original Rollback text by the fixer, not confirmed by the service owner.
