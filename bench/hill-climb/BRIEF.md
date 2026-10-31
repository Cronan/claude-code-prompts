# Benchmark brief (identical for every contender)

You are running one review-and-fix loop skill on a small Python library, as a user would.

- Repository under review: REPO (a git repo, one commit on `master`, clean tree). The whole library is the change under review: there is no earlier base, so where your skill wants a diff against `main`, treat the full tree as the diff and review every file.
- Stated intent: the four requirements in REPO/README.md. Verifier: `python3 -m pytest -q` run in REPO. Public signatures (`RateLimiter(rate, burst, clock=)`, `SlidingWindow(limit, window, clock=)`, `allow(key) -> bool`, `reset(key)`, `stats`, `load_config(dict) -> Config`, `ConfigError`) and the existing passing tests are frozen: fixes may not change them, though tests may be added or made stricter.
- Skill to follow: SKILL. Follow it literally, step by step, including its stopping rule and cap. Where it says to spawn a reviewer, use the Agent tool with a fresh subagent and give that subagent only what the skill says it gets. Where it invokes an external CLI (`claude -p`, `codex`) that is not installed, substitute an Agent subagent with the same prompt and the same tool restrictions, and say so in your report. Where it asks the user for confirmation, treat it as given (`confirm=yes`, "go"). Where it offers a round cap, use 3.
- Do not read anything under /home/claude/bench other than REPO and SKILL (and any files SKILL itself names). Do not read other skills. Do not push, create branches or change the remote.
- Save every reviewer or critic report you receive, verbatim, as OUT/reports/round<N>-<role>.md, and every fix list you act on as OUT/reports/round<N>-fixlist.md.
- When your skill's stopping rule fires, write OUT/REPORT.md containing: which rule stopped you; a table of rounds with findings counted per round; the number of Agent (subagent) calls you made and which model each used; what you fixed, file by file; what remains unfixed and why; and the final output of the verifier.

Work only inside REPO and OUT.
