# Round 3 fix list

Source: reports/round3-reviewer.md (sonnet, read-only).

No fixes applied. Round 3 was the third iteration and the cap (3) fired with findings open; per the skill's guard, the loop stops here and hands the findings to the user. Disposition below is the operator's assessment of each open finding, not a change.

1. Concurrency tests would likely pass without the lock -> open. A deterministic pin would need to inject a yield between the read and the write, which needs a test seam in the frozen class; the clock-read-under-lock test is the only reliable pin.
2. `cutoff < now` guard denies valid tiny windows against large clocks (window=1e-9 with time.time) -> open; agreed, the guard added in round 2 is too strict. Fix would be to drop `cutoff < now` and keep only `math.isfinite(cutoff)`, with window<=0 denied by an explicit `self.window > 0` check instead.
3. Non-integral `limit` (2.5) admits 3 -> open; agreed, fail-closed check on limit missing in SlidingWindow.allow.
4. `burst` integrality checked after float conversion, so 2**53+1 is silently altered -> open; agreed, check integrality on the original value.
5. Accepted/rejected inputs changed beyond the list (MappingProxyType, "5.0", b"1") -> partly disputed: MappingProxyType and Decimal were round 2 findings 3 and 4 from the same reviewer model, so this is the oscillation the skill warns about; a user decision is needed on how wide "mapping" and "number" should be.
6. Clock going backwards stores negative tokens -> open; fail-closed, not unsafe, and out of the four README requirements; clamp `elapsed` at 0 if wanted.
7. README not updated for new rejection rules -> open; not in the skill argument, but cheap.
8. `except Exception` does not catch BaseException -> no action recommended; swallowing SystemExit/KeyboardInterrupt would be wrong.
