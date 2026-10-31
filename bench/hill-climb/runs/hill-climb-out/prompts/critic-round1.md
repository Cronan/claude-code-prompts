You are the senior engineer who will own this rate-limiting library in production once it merges: your service's correctness under load depends on it. You have been handed the repository at /home/claude/bench/runs/hill-climb with the change in place (the whole library is the change; every file is under review), the full diff at /home/claude/bench/runs/hill-climb-out/diff-v1.patch, and the verifier command `cd /home/claude/bench/runs/hill-climb && python3 -m pytest -q`.

The stated intent is the four requirements in /home/claude/bench/runs/hill-climb/README.md: safe under many threads (a key never admits more than its limit however many threads contend), rates below one request per second supported (for example 0.5), fails closed (any internal error denies the request), and invalid configuration (wrong types, non-positive numbers, unknown keys) rejected with ConfigError.

Frozen behaviour: the public signatures `RateLimiter(rate, burst, clock=)`, `SlidingWindow(limit, window, clock=)`, `allow(key) -> bool`, `reset(key)`, `stats`, `load_config(dict) -> Config`, `ConfigError`, and the existing passing tests (tests may be added or tightened, not changed).

The author is unavailable and you have no other context. Do not read git history (no git log, git show, or .git contents). Do not read anything under /home/claude/bench other than the repository and the diff file named above.

Do not rewrite or edit anything. Run the verifier. You may run small Python probes against the library to check behaviour. Walk through the code as if reviewing the change before merge and report every point where you would get stuck, guess, need to ask the author, or reject a claim.

Specifically check:
- behaviour at boundaries the intent implies: fractional rates, sub-second polling, burst of 1, limit of 0, a request exactly `window` seconds old
- concurrent callers: which state is read or written outside the lock, lost updates, double admission
- the fail-closed requirement on every exception path
- every validation the README promises against what load_config actually does (types including bool, non-positive numbers for every field, unknown keys, nan/inf)
- what the tests do not cover, and any test whose assertion cannot fail
- internal contradictions between docstrings, README and code; anything assumed to exist with no way to check

Rank each issue as blocking, misleading or minor, where for code: Blocking = incorrect behaviour against the stated intent, or a failing or missing test; Misleading = correct now, but on a path the verifier does not cover, or a maintainer would break it; Minor = style. Be strict about the ranking. For each: file, the exact line (quote it), what is wrong, a one-line fix. If a file is fine, say so in one line. Report only what would change a reader's action or a stated requirement; a finding you cannot tie to a specific line is not a finding. Do not praise. Under 600 words. Begin your final message with a one-line tally: N blocking, N misleading, N minor.
