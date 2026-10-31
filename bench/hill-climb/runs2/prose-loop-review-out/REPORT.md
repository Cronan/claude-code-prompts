## /loop-review report

**Goal:** make the ingest key rotation runbook executable by the on-call engineer without asking the author anything. **Scope:** /home/claude/bench/runs2/prose-loop-review/RUNBOOK.md (the whole artefact; no code). **Rounds:** 3 of 3, stopped because: **Cap** (round 3 equals max_rounds). The Done rule would not have fired on its own: one confirmed medium finding (step 6 abort path leaves the service stopped) remains as an Ask.

**Resumed run.** The original session died during round 3, after reading the four round-3 reviewer reports and applying the one blocker fix (the last recorded action is the Edit to RUNBOOK.md at 15:45:47 UTC; RUNBOOK.v3.md, the pre-fix copy, was saved at 15:45:41). A second session resumed from that point: it did not run any reviewer process, re-derived the round-3 synthesis from the four saved reports (reports/round3-fixlist.md), verified the applied fix, re-ran the three frozen checks, and wrote this report. Everything from round 1 through the round-3 reviewer launches is taken from the saved reports, fix lists, briefs and the original session's log.

### How the skill was adapted to a prose artefact
- "Code" is the Markdown runbook; "file:line" is RUNBOOK.md:line; "code paths" are the steps the engineer follows; "tests" are the verification steps the runbook gives the engineer; "UI" is the document as read. Reviewers were told this in every brief.
- "Diff against main" is the whole file (one commit, a29dc6a).
- No Agent tool: each reviewer ran as `claude -p --no-session-persistence --model <model> --disallowedTools Bash,Edit,Write -- "<agent body>\n---\n<brief>"`, all four in parallel per round, output captured verbatim to reports/round<N>-<role>.md. The agent bodies and per-agent models came from /home/claude/bench/skills/loop-review-agents.md, which the skill names.
- Checks: the brief's three frozen mechanical checks, scripted (line count <80, `## ` heading order, continuous step numbering). "Verify at the source" was adapted to dry-running the runbook's shell lines against a dummy keys.yaml in the scratchpad (never against a real host). No rendered evidence: no UI, no browser.
- Cost gate: confirmation treated as given per the brief.

### Baseline
- Revision a29dc6a (`runbook v1`), branch master, baseline dirty list: none.
- No CLAUDE.md or AGENTS.md. No manifests.
- Checks before: 54 lines (<80) PASS; section order PASS; steps 1-14 continuous PASS. "No automated checks found" beyond these three; verification manual plus dry runs.
- Definition of done: (1) every step names the exact command, path, field or UI location it needs and no two parts of the document contradict each other; (2) every judgement step ("verify", "acceptable") is replaced by an observable check with a stated threshold or expected output; (3) Rollback can be performed with only the information the runbook itself tells the engineer to capture.

### Reviewer processes
12 reviewer processes in total, 4 per round, none retried, none unavailable. Models per the agent definitions:

| Role | Model | Rounds |
|---|---|---|
| loop-tester | sonnet | 1, 2, 3 |
| loop-builder | sonnet | 1, 2, 3 |
| loop-architect | opus | 1, 2, 3 |
| loop-design-critic | sonnet | 1, 2, 3 |

Model names are the aliases passed on the command line; the exact model IDs they resolved to were not captured. Round 1 stderr carried only a harmless "no stdin data received" warning for three processes; all outputs were usable. No separate verifier processes were run (the skill has none; the main session verified).

### Changes
All in RUNBOOK.md (54 -> 68 lines). `git diff` shows every change; RUNBOOK.v1.md (= HEAD), v2 (after round 1) and v3 (after round 2) sit beside it for comparison.

Round 1 (round1-fixlist.md):
- Step 5: `restart` -> `stop`, plus `systemctl is-active` expecting `inactive` (T-1a, B-1, A-2, D-2). Previously step 8's `start` was a no-op on a running unit.
- Step 6: path corrected to `/etc/ingest/config/keys.yaml` (T-1b, B-2a, A-1, D-3a); `NEW_KEY` set via `read -rs` with sed-escaping and `|` delimiter (T-2, B-2b, A-4, D-3b); `cp -p` backup before the write (T-3, B-3, A-3, D-1, B-4).
- Step 7: asserts the exact `api_key:` line occurs once, `${NEW_KEY:?empty}` aborts on an unset key (T-2 group).
- Steps 9 and 10: judgement steps replaced by `is-active` = `active`, `journalctl -p err` empty, lag <= 8 s for 5 consecutive minutes, 15-minute deadline from step 8 (T-4, B-5, A-5, D-4).
- Step 11: deletes the old key only after step 10 passes, and removes the backup; the contradictory "24 hours" claim removed (T-3 group).
- Step 4: UTC on the date, "note the old key name"; step 14: host and destination for the journal output; Rollback preamble: compromised-key guard (T-5, D-5, partial).

Round 2 (round2-fixlist.md):
- Step 6: backup guarded by `test ! -e .bak && cp && echo BACKUP_OK` with a stop instruction; same-SSH-session requirement stated (T-1, B-1, A-2, D-2; A-5).
- Step 7: "Do not re-run step 6" (T-1 group).
- Step 8 prints the start time with `date -u '+%F %T'`; step 9 uses it as `--since` and names `-- No entries --` as the pass output (T-3).
- Step 10: threshold allows the step 2 baseline if higher (A-3).
- Step 13: removes the `.bak` after restoring; "if step 9 fails again, go to step 14" (T-1 group, B-2).
- Rollback preamble: compromised path leaves the service stopped and deletes the old key in the Vendor Console before paging (T-2, A-1, D-1).

Round 3 (round3-fixlist.md, final round, blocker only):
- Step 13: start line becomes `sudo systemctl start ingest.service && date -u '+%F %T'`, and the text says "repeat step 9 using the time printed here as `<start>`" (T-1, B-1, A-1, D-1, all four reviewers, blocker). This fixes a defect the round-2 change to step 9 introduced: the repeated step 9 had no usable `<start>`, so a correct rollback would always "fail" and page the lead. Applied by the original session; verified by the resumed session.

No fix exceeded about 30 changed lines; the round-1 set is the largest because the original had three blockers in steps 5-7 plus two judgement steps.

### Verification
- Checks after (resumed session, final file): 68 lines (<80) PASS; section order `Layout, Before you start, Rotation, Rollback, Notes` PASS; steps 1-14 continuous PASS. 3 of 3 pass, as they did before every round.
- Dry runs on a dummy directory (never a real host), recorded in the round 2 and 3 briefs and repeated for the round-3 fix: the step 6 backup line prints `BACKUP_OK` once and nothing on a second run or when `cp` fails; keys containing `/ & | \ . * [ ]` round-trip through step 6 and give count 1 in step 7; an unset `NEW_KEY` aborts step 7 with "NEW_KEY: empty"; a missing or wrong `api_key:` line gives count 0; the step 13 chain restores the old value, removes the `.bak` and prints exactly one `YYYY-MM-DD HH:MM:SS` line; `journalctl --since` accepts that format (prints `-- No entries --`, not a parse error) and with no matches prints exactly `-- No entries --`.
- Rendered evidence: none, source only (Markdown document, no UI).
- Not run: anything against a real ingest host, Vendor Console or Grafana. The runbook's references to the `ingest-rotator` role, the dashboard and panel names, the `#ingest-ops` channel and the PyYAML availability for the `ingest` user cannot be verified from the document.
- **Fixes not seen by any reviewer:** the round-3 change to step 13 (two lines). It is a blocker fix of the shape all four reviewers proposed, and it was verified by dry run and read-through in both Rollback entry paths, but no reviewer has read the final text.

### Per round
- Round 1: tester, builder, architect, design critic ran (5+5+5+5 findings). Accepted 6 merged (18 IDs), rejected 1, asked 0 (one sub-item to Needs your decision), backlogged 3.
- Round 2: all four ran (4+3+5+2 findings). Accepted 6 merged (10 IDs), rejected 0, asked 1 merged (3 IDs), backlogged 2, 1 unverified environment assumption to Needs your decision.
- Round 3: all four ran (3+1+3+1 findings). Accepted 1 merged (4 IDs, blocker), rejected 0, asked 1 merged (T-2, A-2, B note), 3 remaining issues (low, final-round rule), backlogged 1.

### Remaining issues
- Step 10 threshold wording: "at or below 8 s (or below the step 2 value, if that was higher)" is inclusive in one clause and strict in the other (round 3 A-3, low). Ambiguous only when lag sits exactly at the baseline. One-word fix ("at or below"), deferred because it changes the pass condition in the final round.
- Step 11: no instruction if `rm keys.yaml.bak` fails (round 3 T-3, low). A leftover `.bak` makes the next rotation's step 6 guard fail and send the engineer to step 14; the guard makes this safe but noisy.
- Compromised path leaves the old secret in `keys.yaml.bak` on the host (round 3 architect note, low). Step 13 is the only place the `.bak` is removed and the compromised path skips it; the key is deleted at the vendor. Also trips the step 6 guard on the next rotation.
- Partial from round 1 (T-5): the platform lead's pager or channel is still not named; "page the platform lead" cannot be made executable from the document alone.
- Expected duration "20 minutes" versus a possible 15-minute wait in step 10 plus a rollback (round 1 architect note, minor).

### Needs your decision
- **Step 6 abort path leaves ingest stopped** (round 3 T-2, A-2, medium, confirmed by trace): if `BACKUP_OK` is not printed the engineer goes to step 14, which only pages and collects logs; the service was stopped in step 5 and nothing restarts it. The live file is untouched on this path, so `sudo systemctl start ingest.service` before paging is safe unless the key is compromised. Not applied: it changes what the engineer does and this was the final round. Impact: an avoidable outage lasting until the lead answers.
- **Unused step 4 key after a rollback** (round 2 T-4, B-3, A-4): the new key stays live in the Vendor Console and a same-day retry would reuse its name. Delete it in Rollback, or keep it and record the name; this is credential policy.
- **Outage on the compromised path**: the runbook now leaves the service stopped and deletes the old key before paging. This follows the document's own stated priority (rotate immediately if compromised) but implies an outage the author should confirm.
- **PyYAML for the `ingest` user**: step 7's `python3 -c "import yaml..."` was in the original and is unverified from the document.
- **Platform lead's pager or channel name**: not in the document; cannot be supplied by the loop.

### Rejected suggestions (with reasons)
- Round 1 D-1: paste the old secret into the change ticket as the rollback source. Puts a live secret in a ticket when an on-host backup suffices.
- Round 1 A-1 fix shape: introduce a `$KEY_FILE` variable. Structural; the literal path correction removes the defect (moved to backlog).
- Round 1 architect note: 20-minute estimate vs 15-minute wait. Minor; listed above under Remaining issues for completeness.
- Round 2 A-2 fix shape: `cmp` after the copy. The `test ! -e` gate before the write is smaller and prevents the overwrite rather than detecting it.
- Round 2 "restart from step 6" after a dropped SSH session. Collides with the one-backup rule; "go to Rollback" used instead.

### Feature backlog
- `$KEY_FILE` variable for the config path (round 1 A-1).
- Pre-flight writability test of the config directory (round 1 architect IDEA).
- Keep the secret out of argv and shell history (round 1 tester and design critic notes; `read -rs` already keeps it off the command line, but it is still expanded into the sed argv).
- Announce rollback in `#ingest-ops` (round 2 architect note).
- Say what happens to buffered upstream data during the stop/start window (round 2 tester note).
- Re-check lag after a restore when Rollback was entered from step 10 (round 3 architect note).

Nothing was committed, pushed or branched. `git diff` in /home/claude/bench/runs2/prose-loop-review shows every change to RUNBOOK.md; RUNBOOK.v1.md, v2 and v3 are untracked comparison copies. No browser was used and no files were created inside the repository other than those copies.
