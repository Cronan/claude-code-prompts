# Reviewloop report: ingest key rotation runbook

Skill argument: make the ingest key rotation runbook executable by the on-call engineer without asking the author anything.

## Stopping rule

Iteration cap (3, as the brief instructed where the skill offers one; the skill's own default is 5). The loop did not converge: the round-3 pass returned 11 findings. Per the skill's guard, the open findings are handed over with what was tried (reports/round3-fixlist.md). No oscillation occurred: no fixed finding reappeared. Two findings (no Grafana URL, no paging method) recurred in all three rounds because they were deliberately rejected each time as organisational knowledge the on-call engineer has independently; inventing a URL or contact would be fabrication.

## Rounds

| Round | Reviewer findings | Applied | Rejected |
|---|---|---|---|
| 1 | 14 | 12 | 2 (paging method; `write:feed` note is pre-existing, not scope creep) |
| 2 | 12 | 11 | 1 (Grafana URL / paging method) |
| 3 | 11 | 0 (cap reached) | 1 (same residual) |

Between round 2 fixes and the round 3 pass I also tested the new commands on scratch data and corrected one defect the reviewer had not seen: `cp -n` exits 0 when it skips an existing file, so the step 7 "do not overwrite an existing backup" guard did not work; rewritten as `test ! -e ... && cp -p ...`. Step 10 was also given an explicit failure path at the same time.

## Reviewer processes

Three, one per round, each `claude -p --no-session-persistence --model sonnet --disallowedTools Bash,Edit,Write`, given only the acceptance list, the adapted checklist groups and the full numbered runbook text. Verbatim outputs: reports/round1-reviewer.md, round2-reviewer.md, round3-reviewer.md. Fix lists: reports/round1-fixlist.md, round2-fixlist.md, round3-fixlist.md.

## Adaptations of the code-oriented skill

- "Diff" = the whole RUNBOOK.md (one commit, clean tree, no untracked files). Reviewers received the file with line numbers inline rather than running git.
- Acceptance list (step 0) derived from the skill argument: seven checkable items covering self-sufficiency, Layout/command consistency, prose/command agreement, concrete checks with bounded waits, executable rollback, the frozen mechanical constraints, and no scope creep.
- "Build/test" = the three frozen mechanical checks (line count, section order, continuous numbering), run after every edit, plus executing the Python one-liners against a scratch keys.yaml containing sed metacharacters.
- Subagent = fresh `claude -p` process; confirmations treated as given.

## What changed (v1 -> final)

Original kept at RUNBOOK.v1.md, round-1 output at RUNBOOK.v2.md, final at RUNBOOK.md (65 lines, 18 steps, section order intact).

- Step "stop the service" ran `systemctl restart`; fixed, then superseded: the service is now left running on the old key until the new file is written and verified, then restarted once.
- sed path `/etc/ingest/keys.yaml` corrected to `/etc/ingest/config/keys.yaml`; sed later replaced by a Python in-place rewrite that tolerates `|`, `&`, `\` in the secret and preserves owner/mode; verification parses the YAML and compares `api_key` to the secret, and checks `ingest:ingest 600`.
- `$NEW_KEY` now defined via `read -rs` and unset after verification (but see open finding 1).
- Backup of keys.yaml added before editing; refuses to overwrite an existing backup; rollback restores the backup instead of asking for an unobtainable old secret.
- Old key identified by name in the ticket before rotation (exactly one `ingest-prod-*` key expected); deletion moved to after the observation window so rollback remains possible; unsupported "valid for 24 hours" claim removed.
- Verification step replaced by `is-active` plus a journal count with stated good values; lag wait bounded (15 minutes, 5 consecutive minutes in range, 60 s threshold as immediate rollback trigger).
- Rollback: restart rather than start; compromised key is not restored; new key deleted on rollback; ticket `<id>` defined in step 1; `YYYYMMDD` is UTC.

## What remains (open, from round 3)

1. BLOCKER: `read -rs NEW_KEY` does not export, so `sudo --preserve-env=NEW_KEY` passes nothing and steps 9 and 10 fail with `KeyError`. Confirmed by shell test. Fix is `export NEW_KEY` in step 8 (and sudoers must allow `--preserve-env`). The final runbook is therefore not executable as written at step 9.
2. Step 9 has no failure path; `write_text` truncates before writing.
3. "Repeat step 8" after an SSH drop is impossible (secret shown once); same-day key-name collision on retry.
4. Journal grep `auth|401` can match benign lines and overlaps shutdown logs; the service's actual rejected-key log line is unknown (author input).
5. Compromised-key path leaves `.bak` on disk, new key live, no resume instruction.
6. Pre-flight for existing `.bak` happens after the new key is created; error text conflates causes.
7. "Repeat the checks in step 11" would restart twice; `.bak` removed before restored state is verified.
8. PyYAML on root's python3 assumed (inherited from v1).
9. Whether the old key stays valid after a new one is issued is vendor behaviour the loop cannot verify (author input).
10. Step 4 baseline unused in the lag criterion.
11. Minor: step 7 "SSH to the service host" redundant with Layout.
Residual by decision: Grafana URL and paging mechanism not added.
