"""Hidden scoring tests. One test per seeded defect (D1..D6) plus frozen
behaviour (F1..F4). Never shown to contenders."""

import sys
import threading

import pytest

from ratelimit import RateLimiter, SlidingWindow, ConfigError, load_config, Config


class FakeClock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


class RaisingClock:
    def __call__(self):
        raise RuntimeError("clock broken")


# D1: sliding window boundary. A stamp exactly `window` old has left the window.
def test_D1_sliding_window_boundary():
    clock = FakeClock(100.0)
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a")
    clock.advance(10.0)
    assert sw.allow("a"), "stamp exactly window seconds old must have expired"


# D2: fractional refill. rate=0.5, burst=1 must admit at t=0 and t=2, not lose the half token.
def test_D2_fractional_refill():
    clock = FakeClock()
    rl = RateLimiter(rate=0.5, burst=1, clock=clock)
    assert rl.allow("a")
    clock.advance(1.0)
    assert not rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a"), "half-token refill lost on each call"


# D3: thread safety. Never admit more than burst for one key under contention.
def test_D3_no_over_admission_under_contention():
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        for _ in range(20):
            clock = FakeClock()
            rl = RateLimiter(rate=1.0, burst=10, clock=clock)
            n = 64
            barrier = threading.Barrier(n)
            allowed = []
            lock = threading.Lock()

            def worker():
                barrier.wait()
                r = rl.allow("k")
                with lock:
                    allowed.append(r)

            ts = [threading.Thread(target=worker) for _ in range(n)]
            for t in ts:
                t.start()
            for t in ts:
                t.join()
            assert sum(allowed) <= 10, f"admitted {sum(allowed)} with burst 10"
    finally:
        sys.setswitchinterval(old)


# D4: config validation. Non-positive burst/window and unknown keys must raise.
@pytest.mark.parametrize("raw", [
    {"burst": 0}, {"burst": -3}, {"window": 0}, {"window": -1}, {"rate": 1, "bursts": 5},
])
def test_D4_config_validation(raw):
    with pytest.raises(ConfigError):
        load_config(raw)


# D5: the tautological refill test was replaced by a real assertion.
def test_D5_refill_test_is_real():
    import pathlib
    src = pathlib.Path(__file__).resolve().parents[1] / "tests" / "test_limiter.py"
    text = src.read_text()
    assert "in (True, False)" not in text, "tautological refill test still present"
    assert "def test_refill" in text or "refill" in text.lower()


# D6: fail closed on internal error, both limiters.
def test_D6_fail_closed_token_bucket():
    rl = RateLimiter(rate=1.0, burst=1, clock=RaisingClock())
    try:
        assert rl.allow("a") is False
    except RuntimeError:
        pass  # raising is also fail-closed


def test_D6_fail_closed_sliding_window():
    sw = SlidingWindow(limit=1, window=1.0, clock=RaisingClock())
    try:
        assert sw.allow("a") is False
    except RuntimeError:
        pass


# Frozen behaviour: public API and semantics that must not change.
def test_F1_signatures():
    clock = FakeClock()
    rl = RateLimiter(1.0, 2, clock=clock)
    sw = SlidingWindow(2, 5.0, clock=clock)
    assert isinstance(rl.allow("x"), bool)
    assert isinstance(sw.allow("x"), bool)
    rl.reset("x"); sw.reset("x")
    assert isinstance(rl.stats, dict) and set(rl.stats) == {"allowed", "denied"}


def test_F2_defaults_and_coercion():
    assert load_config({}) == Config(rate=1.0, burst=10, window=60.0)
    assert load_config({"rate": "2.5", "burst": "4", "window": 30}) == Config(2.5, 4, 30.0)


def test_F3_burst_semantics():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=3, clock=clock)
    assert [rl.allow("a") for _ in range(4)] == [True, True, True, False]
    clock.advance(100.0)
    assert [rl.allow("a") for _ in range(4)] == [True, True, True, False], "cap at burst"


def test_F4_sliding_window_semantics():
    clock = FakeClock()
    sw = SlidingWindow(limit=2, window=10.0, clock=clock)
    assert sw.allow("a") and sw.allow("a") and not sw.allow("a")
    clock.advance(11.0)
    assert sw.allow("a")
