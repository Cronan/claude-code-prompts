# Benchmark brief

You are running one review-and-fix loop skill on an operational runbook, as a user would.

- Artefact under review: REPO/RUNBOOK.md (git, one commit on `master`). It is an executable document: the on-call engineer must be able to perform it without asking the author anything. That is the stated intent. Where your skill assumes code, a diff, or a test command, adapt as best you can and say how in your report; the "diff against main" is the whole file. There is no automated verifier; the only mechanical checks are: under 80 lines, section order unchanged (Layout, Before you start, Rotation, Rollback, Notes), step numbering continuous. Those are frozen.
- Skill to follow: SKILL. Follow it literally, including its stopping rule and cap (use 3 where it offers one). There is no Agent tool in your session. Where the skill says to spawn a reviewer or critic, run a fresh process: `claude -p --no-session-persistence --model <model> --disallowedTools Bash,Edit,Write -- "<prompt>"`, giving it only what the skill says it gets. Where the skill asks for confirmation, treat it as given.
- Do not read anything under /home/claude/bench other than REPO and SKILL (and files SKILL names). Do not push or create branches.
- Save every reviewer/critic/verifier report verbatim as OUT/reports/round<N>-<role>.md and every fix list as OUT/reports/round<N>-fixlist.md. Leave the final runbook at REPO/RUNBOOK.md (versioned copies beside it are fine).
- When the stopping rule fires, write OUT/REPORT.md (use the shell if the Write tool refuses): which rule stopped you; rounds with findings per round; number of reviewer processes and model each; what you changed; what remains.
