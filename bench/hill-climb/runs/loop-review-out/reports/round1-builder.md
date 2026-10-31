NOTE: No Agent/Task tool was available in this session, so this review was performed by the orchestrator itself acting in the loop-builder role (read-only: Read/Grep/Glob of the repo), not by a fresh subagent. Model: claude-fable-5-1 (orchestrator), not sonnet.

Brief given: identical to round1-tester.md.

### Builder findings — round 1
B-1 | blocker | ratelimit/limiter.py:49-50, 84-85 | `except Exception:\n    return True` | Fail-open on any fault. | Change both to `return False`. Effort S. Side effect: a buggy clock now denies instead of admitting; that is the documented intent (module docstring :4-5). | pytest; new fail-closed tests. | high
B-2 | blocker | ratelimit/limiter.py:30-47 | `_snapshot` locks only the dict read; mutation at :43/:46 and `self.stats` at :44/:47 are unlocked. | Over-admission under contention; racy stats. | Inline `_snapshot` into `allow` and wrap the whole body in `with self._lock:`; delete `_snapshot` (it has no other callers: grep shows only :38). Diff sketch:
```
-            now = self.clock()
-            tokens, last = self._snapshot(key, now)
-            elapsed = now - last
-            tokens = min(self.burst, tokens + int(elapsed * self.rate))
-            if tokens > 0:
-                tokens -= 1
-                self._buckets[key] = (tokens, now)
-                self.stats["allowed"] += 1
-                return True
-            self._buckets[key] = (tokens, now)
-            self.stats["denied"] += 1
-            return False
+            with self._lock:
+                now = self.clock()
+                tokens, last = self._buckets.get(key, (self.burst, now))
+                tokens = min(self.burst, tokens + (now - last) * self.rate)
+                if tokens >= 1:
+                    self._buckets[key] = (tokens - 1, now)
+                    self.stats["allowed"] += 1
+                    return True
+                self.stats["denied"] += 1
+                return False
```
Effort S. Side effect: the clock is called while holding the lock (fine for monotonic; an injected slow clock would serialise). `_snapshot` is private, so removing it is not a public API change. | pytest + thread test. | high
B-3 | blocker | ratelimit/limiter.py:40 | `int(elapsed * self.rate)` | Sub-1/s rates lose refill credit (see T-3). | Covered by the B-2 sketch: float tokens, `>= 1`, and no write on deny so credit accrues from the last admit with a single multiplication (avoids float drift from repeated 0.1 additions). Effort S. Side effect: `_buckets` values become floats; nothing reads them except `allow`. | New sub-1/s test. | high
B-4 | high | ratelimit/config.py:30-40 | Validation is "whatever float()/int() accept, plus rate > 0". | Invalid configs produce limiters. | Add, in order: unknown-key check (`set(raw) - KNOWN_KEYS`), bool rejection for each present key, integral check for a float `burst`, then after coercion `math.isfinite` and `> 0` for rate and window, `> 0` for burst. Keep string coercion (frozen test_values uses "2.5" and "4"). About 15 added lines, no new public names. Effort S. Side effect: configs that previously loaded with extra keys or burst=0 now raise; that is the stated requirement, not a semantics change. | New config tests. | high
B-5 | medium | ratelimit/limiter.py:74 | `now = self.clock()` before `with self._lock` in SlidingWindow. | Boundary misordering under contention. | Move the clock call inside the lock (one-line move). Effort S. | Inspection; thread test. | med

### Out of scope
- `RateLimiter.__init__`/`SlidingWindow.__init__` accept rate=0 or negative burst directly; README requirement 4 is about `load_config`, so not proposed here.
