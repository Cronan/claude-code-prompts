from ratelimit import RateLimiter, SlidingWindow


class FakeClock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


def test_burst_then_deny():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=3, clock=clock)
    assert [rl.allow("a") for _ in range(4)] == [True, True, True, False]


def test_keys_independent():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    assert rl.allow("b")
    assert not rl.allow("a")


def test_refill():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a") in (True, False)


def test_reset():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    assert not rl.allow("a")
    rl.reset("a")
    assert rl.allow("a")


def test_stats_counts():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    rl.allow("a")
    rl.allow("a")
    assert rl.stats == {"allowed": 1, "denied": 1}


def test_sliding_window_basic():
    clock = FakeClock()
    sw = SlidingWindow(limit=2, window=10.0, clock=clock)
    assert sw.allow("a")
    assert sw.allow("a")
    assert not sw.allow("a")
    clock.advance(11.0)
    assert sw.allow("a")


def test_sliding_window_reset():
    clock = FakeClock()
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a")
    sw.reset("a")
    assert sw.allow("a")


# --- regression tests added by the hardening review ---

import threading

import pytest


class RaisingClock:
    def __call__(self):
        raise ZeroDivisionError("clock failure")


def test_rate_limiter_fails_closed_on_clock_error():
    rl = RateLimiter(rate=1.0, burst=1, clock=RaisingClock())
    assert rl.allow("a") is False


def test_sliding_window_fails_closed_on_clock_error():
    sw = SlidingWindow(limit=1, window=1.0, clock=RaisingClock())
    assert sw.allow("a") is False


def test_sub_one_per_second_refill():
    clock = FakeClock()
    rl = RateLimiter(rate=0.5, burst=1, clock=clock)
    assert rl.allow("a")
    clock.advance(1.0)
    assert not rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a")


def test_fractional_credit_survives_frequent_polling():
    clock = FakeClock()
    rl = RateLimiter(rate=0.1, burst=1, clock=clock)
    assert rl.allow("a")
    for _ in range(9):
        clock.advance(1.0)
        assert not rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a")


def test_refill_strict():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    assert not rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a")


def _hammer(limiter, key, threads, calls_each):
    results = []
    lock = threading.Lock()
    barrier = threading.Barrier(threads)

    def worker():
        barrier.wait()
        mine = [limiter.allow(key) for _ in range(calls_each)]
        with lock:
            results.extend(mine)

    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return results


def test_rate_limiter_never_over_admits_under_contention():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=5, clock=clock)
    results = _hammer(rl, "a", threads=16, calls_each=50)
    assert sum(results) == 5
    assert rl.stats == {"allowed": 5, "denied": 16 * 50 - 5}


def test_sliding_window_never_over_admits_under_contention():
    clock = FakeClock()
    sw = SlidingWindow(limit=5, window=60.0, clock=clock)
    results = _hammer(sw, "a", threads=16, calls_each=50)
    assert sum(results) == 5
